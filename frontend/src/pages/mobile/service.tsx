import React, { useState } from 'react';
import { Box, Grid, Typography, Avatar, Chip } from '@mui/material';
import { Add, Build, CheckCircle, Schedule } from '@mui/icons-material';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton, 
  MobileTable,
  MobileSearchBar 
} from '../../components/mobile';

// Sample service data
const serviceTickets = [
  {
    id: 'SRV-2024-001',
    customer: 'ABC Corp',
    technician: 'John Smith',
    service: 'Equipment Repair',
    status: 'In Progress',
    priority: 'High',
    date: '2024-01-15',
    location: 'Mumbai Office',
  },
  {
    id: 'SRV-2024-002',
    customer: 'XYZ Ltd',
    technician: 'Jane Doe',
    service: 'Maintenance Check',
    status: 'Completed',
    priority: 'Medium',
    date: '2024-01-14',
    location: 'Delhi Branch',
  },
  {
    id: 'SRV-2024-003',
    customer: 'Tech Solutions',
    technician: 'Mike Wilson',
    service: 'Installation',
    status: 'Scheduled',
    priority: 'Low',
    date: '2024-01-16',
    location: 'Bangalore Office',
  },
];

const serviceColumns = [
  {
    key: 'id',
    label: 'Ticket',
    render: (value: string, row: any) => (
      <Box>
        <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
          {value}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {row.service} • {row.location}
        </Typography>
      </Box>
    ),
  },
  {
    key: 'customer',
    label: 'Customer',
    render: (value: string, row: any) => (
      <Box>
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
          {value}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Tech: {row.technician}
        </Typography>
      </Box>
    ),
  },
  {
    key: 'status',
    label: 'Status',
    render: (value: string, row: any) => (
      <Box>
        <Chip
          label={value}
          size="small"
          color={
            value === 'Completed' ? 'success' 
            : value === 'In Progress' ? 'warning' 
            : value === 'Scheduled' ? 'info'
            : 'default'
          }
          sx={{ fontSize: '0.75rem', mb: 0.5 }}
        />
        <Typography variant="caption" sx={{ 
          display: 'block',
          color: row.priority === 'High' ? 'error.main' 
                : row.priority === 'Medium' ? 'warning.main' 
                : 'text.secondary',
          fontWeight: 600,
        }}>
          {row.priority} Priority
        </Typography>
      </Box>
    ),
  },
  {
    key: 'date',
    label: 'Date',
    render: (value: string) => (
      <Typography variant="body2">
        {new Date(value).toLocaleDateString()}
      </Typography>
    ),
  },
];

const MobileService: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredData = serviceTickets.filter(item =>
    item.customer.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.technician.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.service.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const rightActions = (
    <MobileButton
      variant="contained"
      startIcon={<Add />}
      size="small"
    >
      New Ticket
    </MobileButton>
  );

  return (
    <MobileDashboardLayout
      title="Service Management"
      subtitle="Field Service Operations"
      rightActions={rightActions}
      showBottomNav={true}
    >
      {/* Search */}
      <MobileSearchBar
        value={searchQuery}
        onChange={setSearchQuery}
        placeholder="Search tickets, customers..."
      />

      {/* Service Summary */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={3}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main' }}>
                47
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Tickets
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={3}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'warning.main' }}>
                12
              </Typography>
              <Typography variant="caption" color="text.secondary">
                In Progress
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={3}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'success.main' }}>
                28
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Completed
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={3}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'info.main' }}>
                7
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Scheduled
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
      </Grid>

      {/* Service Tickets */}
      <MobileCard title="Recent Service Tickets">
        <MobileTable
          columns={serviceColumns}
          data={filteredData}
          onRowClick={(row) => console.log('Ticket clicked:', row)}
          showChevron={true}
          emptyMessage="No service tickets found"
        />
      </MobileCard>

      {/* Technician Status */}
      <MobileCard title="Technician Status">
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: 1.5,
            borderRadius: 2,
            backgroundColor: 'success.light',
            color: 'success.contrastText',
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar sx={{ bgcolor: 'success.main', width: 32, height: 32 }}>
                <CheckCircle sx={{ fontSize: '1rem' }} />
              </Avatar>
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  John Smith
                </Typography>
                <Typography variant="caption">
                  Available • 3 jobs completed today
                </Typography>
              </Box>
            </Box>
            <Chip label="Available" size="small" color="success" />
          </Box>

          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: 1.5,
            borderRadius: 2,
            backgroundColor: 'warning.light',
            color: 'warning.contrastText',
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar sx={{ bgcolor: 'warning.main', width: 32, height: 32 }}>
                <Build sx={{ fontSize: '1rem' }} />
              </Avatar>
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  Jane Doe
                </Typography>
                <Typography variant="caption">
                  On Job • ABC Corp - Equipment Repair
                </Typography>
              </Box>
            </Box>
            <Chip label="Busy" size="small" color="warning" />
          </Box>

          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: 1.5,
            borderRadius: 2,
            backgroundColor: 'info.light',
            color: 'info.contrastText',
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar sx={{ bgcolor: 'info.main', width: 32, height: 32 }}>
                <Schedule sx={{ fontSize: '1rem' }} />
              </Avatar>
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  Mike Wilson
                </Typography>
                <Typography variant="caption">
                  Scheduled • Tech Solutions - 2:00 PM
                </Typography>
              </Box>
            </Box>
            <Chip label="Scheduled" size="small" color="info" />
          </Box>
        </Box>
      </MobileCard>

      {/* Quick Actions */}
      <MobileCard title="Quick Actions">
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <MobileButton 
              variant="outlined" 
              fullWidth
              startIcon={<Build />}
            >
              Dispatch
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton 
              variant="outlined" 
              fullWidth
              startIcon={<Schedule />}
            >
              Schedule
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              Parts Inventory
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              Service Reports
            </MobileButton>
          </Grid>
        </Grid>
      </MobileCard>
    </MobileDashboardLayout>
  );
};

export default MobileService;