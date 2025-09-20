// frontend/src/pages/service-desk/index.tsx
// Comprehensive Service Desk Dashboard with enhanced integration
import React, { useState, useEffect } from "react";
import {
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Divider,
  FormControl,
  Grid,
  InputAdornment,
  InputLabel,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  MenuItem,
  Paper,
  Select,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
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
} from "@mui/icons-material";
import { useAuth } from "@/context/AuthContext";
import { serviceDeskService } from '@/services/serviceDeskService';
import { Ticket, ChatbotConversation, ServiceDeskAnalytics } from '@/services/serviceDeskService';
import CreateTicketModal from '@/components/CreateTicketModal';

const ticketStatusColors: Record<string, string> = {
  open: "error",
  in_progress: "warning",
  resolved: "success",
  closed: "primary",
  cancelled: "default",
};
const priorityColors: Record<string, string> = {
  low: "success",
  medium: "info",
  high: "warning",
  urgent: "error",
};
const conversationStatusColors: Record<string, string> = {
  active: "info",
  escalated: "warning",
  resolved: "success",
  closed: "default",
};
export default function ServiceDeskDashboard() {
  const { _user } = useAuth();
  const [currentTab, setCurrentTab] = useState(0);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [conversations, setConversations] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<ServiceDeskAnalytics | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [openTicketDialog, setOpenTicketDialog] = useState(false);
  const [selectedPriority, setSelectedPriority] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadServiceDeskData();
  }, []);

  const loadServiceDeskData = async () => {
    setLoading(true);
    try {
      const today = new Date();
      const thirtyDaysAgo = new Date(today);
      thirtyDaysAgo.setDate(today.getDate() - 30);
      const period_start = thirtyDaysAgo.toISOString().split('T')[0];
      const period_end = today.toISOString().split('T')[0];

      const analyticsData = await serviceDeskService.getAnalytics(period_start, period_end);
      setAnalytics(analyticsData);
      const ticketsData = await serviceDeskService.getTickets();
      setTickets(ticketsData);
      const messages = await serviceDeskService.getChatbotConversations();
      const conversationsMap = messages.reduce((acc: Record<string, any>, msg: ChatbotConversation) => {
        if (!acc[msg.session_id]) {
          acc[msg.session_id] = {
            id: msg.id,
            conversation_id: msg.session_id,
            customer_name: msg.metadata?.customer_name || "Anonymous",
            channel: msg.metadata?.channel || "web_chat",
            status: msg.conversation_stage,
            intent: msg.intent_detected,
            escalated_to_human: msg.escalated_to_human,
            started_at: msg.created_at,
            last_message_at: msg.created_at,
          };
        } else {
          acc[msg.session_id].escalated_to_human = acc[msg.session_id].escalated_to_human || msg.escalated_to_human;
          if (new Date(msg.created_at) > new Date(acc[msg.session_id].last_message_at)) {
            acc[msg.session_id].last_message_at = msg.created_at;
          }
          if (new Date(msg.created_at) < new Date(acc[msg.session_id].started_at)) {
            acc[msg.session_id].started_at = msg.created_at;
          }
        }
        return acc;
      }, {});
      setConversations(Object.values(conversationsMap));
    } catch (err) {
      console.error("Error loading service desk data", err);
    } finally {
      setLoading(false);
    }
  };

  const filteredTickets = tickets.filter((ticket) => {
    const matchesSearch =
      ticket.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ticket.ticket_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (ticket.requested_by?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false);
    const matchesPriority =
      !selectedPriority || ticket.priority === selectedPriority;
    const matchesStatus = !selectedStatus || ticket.status === selectedStatus;
    return matchesSearch && matchesPriority && matchesStatus;
  });
  const filteredConversations = conversations.filter(
    (conv) =>
      conv.customer_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      conv.conversation_id.toLowerCase().includes(searchTerm.toLowerCase()),
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
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <ScheduleIcon color="warning" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Avg Resolution Time
                  </Typography>
                  <Typography variant="h5" component="div">
                    {analytics.avg_resolution_time}h
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Avg First Response: {analytics.first_response_time}h
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
                <FeedbackIcon color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Satisfaction Score
                  </Typography>
                  <Typography variant="h5" component="div">
                    {analytics.customer_satisfaction_score}/5
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {analytics.escalation_rate}% Escalation Rate
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
                <ChatIcon color="info" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Chatbot Conversations
                  </Typography>
                  <Typography variant="h5" component="div">
                    {analytics.chatbot_conversations}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {analytics.human_handoffs} Handoffs
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
                  {ticket.category}
                </Typography>
              </TableCell>
              <TableCell>{ticket.requested_by || `Customer ${ticket.customer_id || 'Unknown'}`}</TableCell>
              <TableCell>
                <Chip
                  label={ticket.status.replace("_", " ")}
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
              <TableCell>{ticket.assigned_to ? `User ${ticket.assigned_to}` : "Unassigned"}</TableCell>
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
        {filteredConversations.map((conversation: any, index: number) => (
          <React.Fragment key={conversation.id}>
            <ListItem>
              <ListItemAvatar>
                <Avatar>
                  {conversation.escalated_to_human ? (
                    <PersonIcon />
                  ) : (
                    <SmartToyIcon />
                  )}
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <Typography variant="body1">
                      {conversation.customer_name || "Anonymous"}
                    </Typography>
                    <Chip
                      label={conversation.status}
                      color={
                        conversationStatusColors[conversation.status] as any
                      }
                      size="small"
                    />
                    <Chip
                      label={conversation.channel.replace("_", " ")}
                      variant="outlined"
                      size="small"
                    />
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="body2" color="textSecondary">
                      Intent:{" "}
                      {conversation.intent?.replace("_", " ") || "Unknown"}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Started:{" "}
                      {new Date(conversation.started_at).toLocaleString()}
                      {conversation.last_message_at &&
                        ` • Last message: ${new Date(conversation.last_message_at).toLocaleString()}`}
                    </Typography>
                  </Box>
                }
              />
              {conversation.status === "resolved" && (
                <CheckCircleIcon color="success" />
              )}
            </ListItem>
            {index < filteredConversations.length - 1 && (
              <Divider variant="inset" component="li" />
            )}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
  if (loading) {
    return <Box sx={{ p: 3 }}><Typography>Loading...</Typography></Box>;
  }
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
          Service Desk Dashboard
        </Typography>
        <Box sx={{ display: "flex", gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenTicketDialog(true)}
          >
            Create Ticket
          </Button>
          <Button variant="outlined" startIcon={<AssessmentIcon />}>
            Reports
          </Button>
        </Box>
      </Box>
      {renderAnalyticsCards()}
      <Card>
        <CardContent>
          <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
            <Tabs
              value={currentTab}
              onChange={(_, newValue) => setCurrentTab(newValue)}
            >
              <Tab label="Tickets" />
              <Tab label="Chatbot Conversations" />
            </Tabs>
          </Box>
          <Box sx={{ display: "flex", gap: 2, mb: 2, flexWrap: "wrap" }}>
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
      <CreateTicketModal
        open={openTicketDialog}
        onClose={() => setOpenTicketDialog(false)}
        onSuccess={loadServiceDeskData}
        organizationId={_user?.organization_id || 0}
      />
    </Box>
  );
}