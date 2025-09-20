// frontend/src/pages/service-desk/tickets.tsx
import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Fab
} from '@mui/material';
import { 
  Assignment, 
  Add, 
  Schedule,
  CheckCircle,
  Error,
  Warning,
  Edit,
  Visibility,
  Timelapse
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';
import CreateTicketModal from '../../components/CreateTicketModal';
import { serviceDeskService } from '../../services/serviceDeskService';

const ServiceDeskTicketsPage: React.FC = () => {
  const [ticketStats, setTicketStats] = useState({
    total: 0,
    open: 0,
    inProgress: 0,
    resolved: 0,
    avgClosingTime: 0
  });
  const [recentTickets, setRecentTickets] = useState([]);
  const [openCreateModal, setOpenCreateModal] = useState(false);
  const [openEditModal, setOpenEditModal] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const today = new Date();
        const thirtyDaysAgo = new Date(today);
        thirtyDaysAgo.setDate(today.getDate() - 30);
        const period_start = thirtyDaysAgo.toISOString().split('T')[0];
        const period_end = today.toISOString().split('T')[0];

        const analytics = await serviceDeskService.getAnalytics(period_start, period_end);
        setTicketStats({
          total: analytics.total_tickets,
          open: analytics.open_tickets,
          inProgress: analytics.in_progress_tickets,
          resolved: analytics.resolved_tickets,
          avgClosingTime: analytics.average_resolution_time_hours || 0
        });

        const tickets = await serviceDeskService.getTickets(0, 10);
        setRecentTickets(tickets.map(ticket => ({
          id: ticket.id,  // Use actual ID for editing
          ticket_number: ticket.ticket_number,
          title: ticket.title,
          customer: ticket.requested_by || 'Anonymous',
          status: ticket.status,
          priority: ticket.priority,
          assignee: ticket.assigned_to ? `User ${ticket.assigned_to}` : 'Unassigned',
          created: new Date(ticket.created_at).toLocaleString()
        })));
      } catch (error) {
        console.error('Error fetching ticket data:', error);
      }
    };

    fetchData();
  }, []);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'error';
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved': return 'success';
      case 'in_progress': return 'warning';
      case 'open': return 'primary';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'resolved': return <CheckCircle />;
      case 'in_progress': return <Schedule />;
      case 'open': return <Assignment />;
      default: return <Assignment />;
    }
  };

  const handleRowClick = async (ticketId: number) => {
    try {
      const ticket = await serviceDeskService.getTicket(ticketId);
      setSelectedTicket(ticket);
      setOpenEditModal(true);
    } catch (error) {
      console.error('Error fetching ticket for edit:', error);
    }
  };

  const handleEditClose = () => {
    setOpenEditModal(false);
    setSelectedTicket(null);
  };

  const handleEditSuccess = () => {
    handleEditClose();
    // Refresh data
    const fetchData = async () => {
      // ... (reuse fetch logic or extract to function)
    };
    fetchData();
  };

  return (
    <DashboardLayout
      title="Support Tickets"
      subtitle="Manage customer support requests and tickets"
      actions={
        <Button 
          variant="contained" 
          startIcon={<Add />}
          onClick={() => setOpenCreateModal(true)}
        >
          Create Ticket
        </Button>
      }
    >
      <Grid container spacing={3}>
        {/* Ticket Statistics */}
        <Grid item xs={12} md={true}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Assignment sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Total Tickets</Typography>
              </Box>
              <Typography variant="h3" color="primary.main">
                {ticketStats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={true}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Error sx={{ mr: 1, color: 'error.main' }} />
                <Typography variant="h6">Open</Typography>
              </Box>
              <Typography variant="h3" color="error.main">
                {ticketStats.open}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={true}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Warning sx={{ mr: 1, color: 'warning.main' }} />
                <Typography variant="h6">In Progress</Typography>
              </Box>
              <Typography variant="h3" color="warning.main">
                {ticketStats.inProgress}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={true}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CheckCircle sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="h6">Resolved</Typography>
              </Box>
              <Typography variant="h3" color="success.main">
                {ticketStats.resolved}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={true}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Timelapse sx={{ mr: 1, color: 'info.main' }} />
                <Typography variant="h6">Avg Closing Time</Typography>
              </Box>
              <Typography variant="h3" color="info.main">
                {Math.round(ticketStats.avgClosingTime)} hours
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Tickets Table */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Support Tickets
              </Typography>
              <TableContainer>
                <Table sx={{ width: '100%', tableLayout: 'fixed' }}>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ width: '10%' }}>Ticket No.</TableCell>
                      <TableCell sx={{ width: '15%' }}>Customer</TableCell>
                      <TableCell sx={{ width: '10%' }}>Created At</TableCell>
                      <TableCell sx={{ width: '20%' }}>Problem</TableCell>
                      <TableCell sx={{ width: '10%' }}>Status</TableCell>
                      <TableCell sx={{ width: '10%' }}>Priority</TableCell>
                      <TableCell sx={{ width: '15%' }}>Assigned To</TableCell>
                      <TableCell sx={{ width: '10%' }} align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentTickets.map((ticket) => (
                      <TableRow key={ticket.id} onClick={() => handleRowClick(ticket.id)} sx={{ cursor: 'pointer' }}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {ticket.ticket_number}
                          </Typography>
                        </TableCell>
                        <TableCell>{ticket.customer}</TableCell>
                        <TableCell>{ticket.created}</TableCell>
                        <TableCell sx={{ wordBreak: 'break-word' }}>{ticket.title}</TableCell>
                        <TableCell>
                          <Chip 
                            label={ticket.status}
                            color={getStatusColor(ticket.status) as any}
                            size="small"
                            icon={getStatusIcon(ticket.status)}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={ticket.priority}
                            color={getPriorityColor(ticket.priority) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{ticket.assignee}</TableCell>
                        <TableCell align="right">
                          <IconButton size="small">
                            <Visibility />
                          </IconButton>
                          <IconButton size="small">
                            <Edit />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              
              <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                <Button variant="outlined" href="/service-desk/sla">
                  SLA Management
                </Button>
                <Button variant="outlined" href="/service-desk/escalations">
                  Escalations
                </Button>
                <Button variant="outlined" href="/service-desk/knowledge">
                  Knowledge Base
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Fab 
        color="primary" 
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => setOpenCreateModal(true)}
      >
        <Add />
      </Fab>

      <CreateTicketModal 
        open={openCreateModal} 
        onClose={() => setOpenCreateModal(false)} 
      />
      
      <CreateTicketModal 
        open={openEditModal} 
        onClose={handleEditClose}
        mode="edit"
        initialData={selectedTicket}
        onSuccess={handleEditSuccess}
      />
    </DashboardLayout>
  );
};

export default ServiceDeskTicketsPage;