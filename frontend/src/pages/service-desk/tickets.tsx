// pages/service-desk/tickets.tsx
import React from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Grid,
  Alert,
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
  Support,
  TrendingUp,
  Schedule,
  CheckCircle,
  Error,
  Warning,
  Edit,
  Visibility
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';

const ServiceDeskTicketsPage: React.FC = () => {
  const ticketStats = {
    total: 156,
    open: 42,
    inProgress: 28,
    resolved: 86
  };

  const recentTickets = [
    { 
      id: 'TKT-001', 
      title: 'Login issues on mobile app', 
      customer: 'John Smith',
      status: 'open', 
      priority: 'high', 
      created: '2 hours ago',
      assignee: 'Sarah Johnson'
    },
    { 
      id: 'TKT-002', 
      title: 'Report generation error', 
      customer: 'Jane Doe',
      status: 'in-progress', 
      priority: 'medium', 
      created: '1 day ago',
      assignee: 'Mike Wilson'
    },
    { 
      id: 'TKT-003', 
      title: 'Feature request - Dark mode', 
      customer: 'Bob Johnson',
      status: 'resolved', 
      priority: 'low', 
      created: '3 days ago',
      assignee: 'Lisa Chen'
    },
    { 
      id: 'TKT-004', 
      title: 'Database connection timeout', 
      customer: 'Alice Brown',
      status: 'open', 
      priority: 'critical', 
      created: '30 minutes ago',
      assignee: 'Tom Davis'
    },
  ];

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'error';
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'resolved': return 'success';
      case 'in-progress': return 'warning';
      case 'open': return 'primary';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'resolved': return <CheckCircle />;
      case 'in-progress': return <Schedule />;
      case 'open': return <Assignment />;
      default: return <Assignment />;
    }
  };

  return (
    <DashboardLayout
      title="Support Tickets"
      subtitle="Manage customer support requests and tickets"
      actions={
        <Button 
          variant="contained" 
          startIcon={<Add />}
        >
          Create Ticket
        </Button>
      }
    >
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Alert severity="info" sx={{ mb: 3 }}>
            Track and manage customer support tickets. Monitor SLA compliance and response times.
          </Alert>
        </Grid>
        
        {/* Ticket Statistics */}
        <Grid item xs={12} md={3}>
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
        
        <Grid item xs={12} md={3}>
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
        
        <Grid item xs={12} md={3}>
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
        
        <Grid item xs={12} md={3}>
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
        
        {/* Tickets Table */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Support Tickets
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Ticket ID</TableCell>
                      <TableCell>Title</TableCell>
                      <TableCell>Customer</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Priority</TableCell>
                      <TableCell>Assignee</TableCell>
                      <TableCell>Created</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentTickets.map((ticket) => (
                      <TableRow key={ticket.id}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {ticket.id}
                          </Typography>
                        </TableCell>
                        <TableCell>{ticket.title}</TableCell>
                        <TableCell>{ticket.customer}</TableCell>
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
                        <TableCell>{ticket.created}</TableCell>
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
      >
        <Add />
      </Fab>
    </DashboardLayout>
  );
};

export default ServiceDeskTicketsPage;