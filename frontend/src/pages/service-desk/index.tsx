// frontend/src/pages/service-desk/index.tsx
import React, { useState, useEffect } from 'react';
import {
declare function loadServiceDeskData(...args: any[]): any;
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
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Support as SupportIcon,
  Chat as ChatIcon,
  Assessment as AssessmentIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
  SmartToy as SmartToyIcon,
  Feedback as FeedbackIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { useAuth } from '@/context/AuthContext';
interface Ticket {
  id: number;
  ticket_number: string;
  title: string;
  description?: string;
  status: string;
  priority: string;
  ticket_type: string;
  customer_id: number;
  customer_name: string;
  assigned_to_id?: number;
  assigned_to_name?: string;
  created_at: string;
  due_date?: string;
}
interface ChatbotConversation {
  id: number;
  conversation_id: string;
  customer_name?: string;
  channel: string;
  status: string;
  intent?: string;
  escalated_to_human: boolean;
  started_at: string;
  last_message_at?: string;
}
interface ServiceDeskAnalytics {
  total_tickets: number;
  open_tickets: number;
  in_progress_tickets: number;
  resolved_tickets: number;
  tickets_by_priority: Record<string, number>;
  average_resolution_time_hours: number;
  sla_compliance_rate: number;
  customer_satisfaction_score: number;
  first_contact_resolution_rate: number;
}
const ticketStatusColors: Record<string, string> = {
  open: 'error',
  in_progress: 'warning',
  resolved: 'success',
  closed: 'primary',
  cancelled: 'default',
};
const priorityColors: Record<string, string> = {
  low: 'success',
  medium: 'info',
  high: 'warning',
  urgent: 'error',
};
const conversationStatusColors: Record<string, string> = {
  active: 'info',
  escalated: 'warning',
  resolved: 'success',
  closed: 'default',
};
export default function ServiceDeskDashboard() {
const  = useAuth();
  const [currentTab, setCurrentTab] = useState(0);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [conversations, setConversations] = useState<ChatbotConversation[]>([]);
  const [analytics, setAnalytics] = useState<ServiceDeskAnalytics | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [openTicketDialog, setOpenTicketDialog] = useState(false);
  const [selectedPriority, setSelectedPriority] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  useEffect(() => {
    loadServiceDeskData();
  }, []);
  const loadServiceDeskData = async () => {
    setLoading(true);
    try {
      // Simulate API calls - in production these would be real API calls
      const mockTickets: Ticket[] = [
        {
          id: 1,
          ticket_number: 'TKT000001',
          title: 'Software Installation Issue',
          description: 'Unable to install the latest software update',
          status: 'open',
          priority: 'high',
          ticket_type: 'support',
          customer_id: 1,
          customer_name: 'ABC Corp',
          assigned_to_id: 1,
          assigned_to_name: 'John Smith',
          created_at: '2024-08-27T09:00:00Z',
          due_date: '2024-08-28T17:00:00Z',
        },
        {
          id: 2,
          ticket_number: 'TKT000002',
          title: 'Printer Maintenance Request',
          description: 'Regular maintenance for office printer',
          status: 'in_progress',
          priority: 'medium',
          ticket_type: 'maintenance',
          customer_id: 2,
          customer_name: 'XYZ Inc',
          assigned_to_id: 2,
          assigned_to_name: 'Jane Doe',
          created_at: '2024-08-26T14:30:00Z',
          due_date: '2024-08-29T12:00:00Z',
        },
        {
          id: 3,
          ticket_number: 'TKT000003',
          title: 'Network Configuration',
          description: 'Setup new network configuration',
          status: 'resolved',
          priority: 'low',
          ticket_type: 'installation',
          customer_id: 3,
          customer_name: 'Tech Solutions',
          assigned_to_id: 1,
          assigned_to_name: 'John Smith',
          created_at: '2024-08-25T10:15:00Z',
        },
      ];
      const mockConversations: ChatbotConversation[] = [
        {
          id: 1,
          conversation_id: 'conv_001',
          customer_name: 'Sarah Johnson',
          channel: 'web_chat',
          status: 'active',
          intent: 'product_inquiry',
          escalated_to_human: false,
          started_at: '2024-08-27T10:30:00Z',
          last_message_at: '2024-08-27T10:35:00Z',
        },
        {
          id: 2,
          conversation_id: 'conv_002',
          customer_name: 'Mike Brown',
          channel: 'whatsapp',
          status: 'escalated',
          intent: 'support_request',
          escalated_to_human: true,
          started_at: '2024-08-27T09:15:00Z',
          last_message_at: '2024-08-27T09:45:00Z',
        },
        {
          id: 3,
          conversation_id: 'conv_003',
          customer_name: 'Lisa Davis',
          channel: 'web_chat',
          status: 'resolved',
          intent: 'billing_inquiry',
          escalated_to_human: false,
          started_at: '2024-08-27T08:00:00Z',
          last_message_at: '2024-08-27T08:15:00Z',
        },
      ];
      const mockAnalytics: ServiceDeskAnalytics = {
        total_tickets: 25,
        open_tickets: 8,
        in_progress_tickets: 12,
        resolved_tickets: 5,
        tickets_by_priority: {
          low: 5,
          medium: 12,
          high: 6,
          urgent: 2,
        },
        average_resolution_time_hours: 18.5,
        sla_compliance_rate: 92.5,
        customer_satisfaction_score: 4.3,
        first_contact_resolution_rate: 68.5,
      };
      setTickets(mockTickets);
      setConversations(mockConversations);
      setAnalytics(mockAnalytics);
    } catch (error) {
      console.error('Error loading service desk data:', error);
    } finally {
      setLoading(false);
    }
  };
  const filteredTickets = tickets.filter((ticket) => {
    const matchesSearch =
      ticket.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.ticket_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.customer_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPriority = !selectedPriority || ticket.priority === selectedPriority;
    const matchesStatus = !selectedStatus || ticket.status === selectedStatus;
    return matchesSearch && matchesPriority && matchesStatus;
  });
  const filteredConversations = conversations.filter((conv) =>
    conv.customer_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    conv.conversation_id.toLowerCase().includes(searchTerm.toLowerCase())
  );
  const renderAnalyticsCards = () => {
    if (!analytics) {return null;}
    return (
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <SupportIcon color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Tickets
                  </Typography>
                  <Typography variant="h5" component="div">
                    {analytics.total_tickets}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {analytics.open_tickets} open
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
                <ScheduleIcon color="warning" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Avg Resolution
                  </Typography>
                  <Typography variant="h5" component="div">
                    {analytics.average_resolution_time_hours}h
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {analytics.sla_compliance_rate}% SLA compliance
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
                <FeedbackIcon color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Satisfaction Score
                  </Typography>
                  <Typography variant="h5" component="div">
                    {analytics.customer_satisfaction_score}/5
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {analytics.first_contact_resolution_rate}% FCR
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
                <ChatIcon color="info" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Chats
                  </Typography>
                  <Typography variant="h5" component="div">
                    {conversations.filter(c => c.status === 'active').length}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {conversations.filter(c => c.escalated_to_human).length} escalated
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };
  const renderTicketsTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Ticket #</TableCell>
            <TableCell>Title</TableCell>
            <TableCell>Customer</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Priority</TableCell>
            <TableCell>Assigned To</TableCell>
            <TableCell>Due Date</TableCell>
            <TableCell>Created</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {filteredTickets.map((ticket) => (
            <TableRow key={ticket.id} hover>
              <TableCell>{ticket.ticket_number}</TableCell>
              <TableCell>
                <Typography variant="body2" fontWeight="medium">
                  {ticket.title}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {ticket.ticket_type}
                </Typography>
              </TableCell>
              <TableCell>{ticket.customer_name}</TableCell>
              <TableCell>
                <Chip
                  label={ticket.status.replace('_', ' ')}
                  color={ticketStatusColors[ticket.status] as any}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Chip
                  label={ticket.priority}
                  color={priorityColors[ticket.priority] as any}
                  size="small"
                  variant="outlined"
                />
              </TableCell>
              <TableCell>{ticket.assigned_to_name || 'Unassigned'}</TableCell>
              <TableCell>
                {ticket.due_date ? (
                  <Typography 
                    variant="body2"
                    color={new Date(ticket.due_date) < new Date() ? 'error' : 'textSecondary'}
                  >
                    {new Date(ticket.due_date).toLocaleDateString()}
                  </Typography>
                ) : '-'}
              </TableCell>
              <TableCell>
                {new Date(ticket.created_at).toLocaleDateString()}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
  const renderConversationsList = () => (
    <Paper>
      <List>
        {filteredConversations.map((conversation, index) => (
          <React.Fragment key={conversation.id}>
            <ListItem>
              <ListItemAvatar>
                <Avatar>
                  {conversation.escalated_to_human ? <PersonIcon /> : <SmartToyIcon />}
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body1">
                      {conversation.customer_name || 'Anonymous'}
                    </Typography>
                    <Chip
                      label={conversation.status}
                      color={conversationStatusColors[conversation.status] as any}
                      size="small"
                    />
                    <Chip
                      label={conversation.channel.replace('_', ' ')}
                      variant="outlined"
                      size="small"
                    />
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="body2" color="textSecondary">
                      Intent: {conversation.intent?.replace('_', ' ') || 'Unknown'}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Started: {new Date(conversation.started_at).toLocaleString()}
                      {conversation.last_message_at && 
                        ` • Last message: ${new Date(conversation.last_message_at).toLocaleString()}`
                      }
                    </Typography>
                  </Box>
                }
              />
              {conversation.status === 'resolved' && (
                <CheckCircleIcon color="success" />
              )}
            </ListItem>
            {index < filteredConversations.length - 1 && <Divider variant="inset" component="li" />}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Service Desk Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenTicketDialog(true)}
          >
            Create Ticket
          </Button>
          <Button
            variant="outlined"
            startIcon={<AssessmentIcon />}
          >
            Reports
          </Button>
        </Box>
      </Box>
      {renderAnalyticsCards()}
      <Card>
        <CardContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
            <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
              <Tab label="Tickets" />
              <Tab label="Chatbot Conversations" />
            </Tabs>
          </Box>
          <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
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
              sx={{ minWidth: 300 }}
            />
            {currentTab === 0 && (
              <>
                <FormControl sx={{ minWidth: 120 }}>
                  <InputLabel>Priority</InputLabel>
                  <Select
                    value={selectedPriority}
                    onChange={(e) => setSelectedPriority(e.target.value)}
                  >
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="low">Low</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="urgent">Urgent</MenuItem>
                  </Select>
                </FormControl>
                <FormControl sx={{ minWidth: 120 }}>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={selectedStatus}
                    onChange={(e) => setSelectedStatus(e.target.value)}
                  >
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="open">Open</MenuItem>
                    <MenuItem value="in_progress">In Progress</MenuItem>
                    <MenuItem value="resolved">Resolved</MenuItem>
                    <MenuItem value="closed">Closed</MenuItem>
                  </Select>
                </FormControl>
              </>
            )}
          </Box>
          {currentTab === 0 && renderTicketsTable()}
          {currentTab === 1 && renderConversationsList()}
        </CardContent>
      </Card>
      {/* Create Ticket Dialog - Placeholder */}
      <Dialog
        open={openTicketDialog}
        onClose={() => setOpenTicketDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create New Ticket</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  label="Title"
                  fullWidth
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Customer</InputLabel>
                  <Select>
                    <MenuItem value="1">ABC Corp</MenuItem>
                    <MenuItem value="2">XYZ Inc</MenuItem>
                    <MenuItem value="3">Tech Solutions</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select defaultValue="medium">
                    <MenuItem value="low">Low</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="urgent">Urgent</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Type</InputLabel>
                  <Select defaultValue="support">
                    <MenuItem value="support">Support</MenuItem>
                    <MenuItem value="maintenance">Maintenance</MenuItem>
                    <MenuItem value="installation">Installation</MenuItem>
                    <MenuItem value="complaint">Complaint</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Due Date"
                  type="datetime-local"
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Description"
                  multiline
                  rows={4}
                  fullWidth
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenTicketDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setOpenTicketDialog(false)}>
            Create Ticket
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}