import React, { useState } from 'react';
import { Box, Grid, Typography, Chip } from '@mui/material';
import { Add, FilterList } from '@mui/icons-material';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton, 
  MobileTable,
  MobileSearchBar 
} from '../../components/mobile';

// Sample sales data
const salesData = [
  {
    id: 'INV-2024-001',
    customer: 'John Doe',
    amount: '₹25,400',
    status: 'Paid',
    date: '2024-01-15',
  },
  {
    id: 'INV-2024-002',
    customer: 'ABC Corp',
    amount: '₹45,000',
    status: 'Pending',
    date: '2024-01-14',
  },
  {
    id: 'INV-2024-003',
    customer: 'XYZ Ltd',
    amount: '₹12,750',
    status: 'Overdue',
    date: '2024-01-12',
  },
];

const salesColumns = [
  {
    key: 'id',
    label: 'Invoice',
    render: (value: string) => (
      <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
        {value}
      </Typography>
    ),
  },
  {
    key: 'customer',
    label: 'Customer',
  },
  {
    key: 'amount',
    label: 'Amount',
    render: (value: string) => (
      <Typography variant="body2" sx={{ fontWeight: 600 }}>
        {value}
      </Typography>
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
          value === 'Paid' ? 'success' 
          : value === 'Pending' ? 'warning' 
          : 'error'
        }
        sx={{ fontSize: '0.75rem' }}
      />
    ),
  },
  {
    key: 'date',
    label: 'Date',
  },
];

const MobileSales: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredData = salesData.filter(item =>
    item.customer.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const rightActions = (
    <MobileButton
      variant="contained"
      startIcon={<Add />}
      size="small"
    >
      New Sale
    </MobileButton>
  );

  return (
    <MobileDashboardLayout
      title="Sales"
      subtitle="Manage your sales and invoices"
      rightActions={rightActions}
      showBottomNav={true}
    >
      {/* Search and Filter */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Box sx={{ flex: 1 }}>
          <MobileSearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Search invoices or customers..."
          />
        </Box>
        <MobileButton
          variant="outlined"
          startIcon={<FilterList />}
          sx={{ minWidth: 'auto', px: 2 }}
        >
          Filter
        </MobileButton>
      </Box>

      {/* Sales Summary */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={4}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'success.main' }}>
                ₹83,150
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Sales
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={4}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'warning.main' }}>
                ₹45,000
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Pending
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={4}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'error.main' }}>
                ₹12,750
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Overdue
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
      </Grid>

      {/* Recent Sales */}
      <MobileCard title="Recent Sales">
        <MobileTable
          columns={salesColumns}
          data={filteredData}
          onRowClick={(row) => console.log('Row clicked:', row)}
          showChevron={true}
          emptyMessage="No sales found"
        />
      </MobileCard>

      {/* Quick Actions */}
      <MobileCard title="Quick Actions">
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              Sales Report
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              Payment Reminder
            </MobileButton>
          </Grid>
        </Grid>
      </MobileCard>
    </MobileDashboardLayout>
  );
};

export default MobileSales;