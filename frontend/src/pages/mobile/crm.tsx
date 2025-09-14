import React, { useState } from 'react';
import { Box, Grid, Typography, Avatar, Chip } from '@mui/material';
import { Add, Call, Email } from '@mui/icons-material';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton, 
  MobileTable,
  MobileSearchBar 
} from '../../components/mobile';

// Sample CRM data
const customersData = [
  {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    phone: '+91 98765 43210',
    company: 'ABC Corp',
    status: 'Active',
    lastContact: '2024-01-15',
  },
  {
    id: 2,
    name: 'Jane Smith',
    email: 'jane@example.com',
    phone: '+91 87654 32109',
    company: 'XYZ Ltd',
    status: 'Lead',
    lastContact: '2024-01-14',
  },
  {
    id: 3,
    name: 'Bob Johnson',
    email: 'bob@example.com',
    phone: '+91 76543 21098',
    company: 'Tech Solutions',
    status: 'Prospect',
    lastContact: '2024-01-12',
  },
];

const crmColumns = [
  {
    key: 'name',
    label: 'Customer',
    render: (value: string, row: any) => (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Avatar sx={{ width: 32, height: 32, fontSize: '0.875rem' }}>
          {value.charAt(0)}
        </Avatar>
        <Box>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            {value}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {row.company}
          </Typography>
        </Box>
      </Box>
    ),
  },
  {
    key: 'email',
    label: 'Contact',
    render: (value: string, row: any) => (
      <Box>
        <Typography variant="body2">{value}</Typography>
        <Typography variant="caption" color="text.secondary">
          {row.phone}
        </Typography>
      </Box>
    ),
  },
  {
    key: 'status',
    label: 'Status',
    render: (value: string) => (
      <Chip
        label={value}
        size="small"
        color={
          value === 'Active' ? 'success' 
          : value === 'Lead' ? 'primary' 
          : 'default'
        }
        sx={{ fontSize: '0.75rem' }}
      />
    ),
  },
  {
    key: 'lastContact',
    label: 'Last Contact',
  },
];

const MobileCRM: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredData = customersData.filter(item =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.company.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const rightActions = (
    <MobileButton
      variant="contained"
      startIcon={<Add />}
      size="small"
    >
      Add Contact
    </MobileButton>
  );

  return (
    <MobileDashboardLayout
      title="CRM"
      subtitle="Customer Relationship Management"
      rightActions={rightActions}
      showBottomNav={true}
    >
      {/* Search */}
      <MobileSearchBar
        value={searchQuery}
        onChange={setSearchQuery}
        placeholder="Search customers, companies..."
      />

      {/* CRM Summary */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={4}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'success.main' }}>
                156
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Active Customers
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={4}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main' }}>
                23
              </Typography>
              <Typography variant="caption" color="text.secondary">
                New Leads
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={4}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'warning.main' }}>
                47
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Follow-ups
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
      </Grid>

      {/* Customer List */}
      <MobileCard title="Recent Customers">
        <MobileTable
          columns={crmColumns}
          data={filteredData}
          onRowClick={(row) => console.log('Customer clicked:', row)}
          showChevron={true}
          emptyMessage="No customers found"
        />
      </MobileCard>

      {/* Quick Actions */}
      <MobileCard title="Quick Actions">
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <MobileButton 
              variant="outlined" 
              fullWidth
              startIcon={<Call />}
            >
              Call Log
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton 
              variant="outlined" 
              fullWidth
              startIcon={<Email />}
            >
              Send Email
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              Lead Pipeline
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              Customer Report
            </MobileButton>
          </Grid>
        </Grid>
      </MobileCard>
    </MobileDashboardLayout>
  );
};

export default MobileCRM;