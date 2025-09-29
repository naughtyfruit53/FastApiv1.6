import React, { useState } from 'react';
import { Box, Grid, Typography, Chip } from '@mui/material';
import { Add, TrendingUp, TrendingDown, AccountBalance } from '@mui/icons-material';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton, 
  MobileTable,
  MobileSearchBar 
} from '../../components/mobile';

// TODO: CRITICAL - Replace hardcoded data with real financial API integration
// TODO: Integrate with financial services (accounts payable, receivable, ledger)
// TODO: Add real-time financial dashboard with live metrics
// TODO: Implement mobile-optimized accounts payable interface
// TODO: Add accounts receivable with customer payment tracking
// TODO: Create touch-friendly financial report viewers (P&L, Balance Sheet, Cash Flow)
// TODO: Implement mobile expense entry and tracking
// TODO: Add quick payment recording interface with barcode scanning
// TODO: Create mobile-optimized charts for financial KPIs
// TODO: Add bank reconciliation mobile workflow
// TODO: Implement budget tracking with mobile alerts and notifications
// TODO: Add financial analytics with drill-down capabilities
// TODO: Implement offline financial data caching
// TODO: Add export functionality (PDF, Excel) for mobile sharing

// Sample finance data - REPLACE WITH REAL API INTEGRATION
const financeData = [
  {
    id: 'TXN-2024-001',
    type: 'Receipt',
    amount: '₹25,400',
    account: 'Sales Account',
    status: 'Cleared',
    date: '2024-01-15',
  },
  {
    id: 'TXN-2024-002',
    type: 'Payment',
    amount: '₹15,000',
    account: 'Purchase Account',
    status: 'Pending',
    date: '2024-01-14',
  },
  {
    id: 'TXN-2024-003',
    type: 'Journal',
    amount: '₹8,750',
    account: 'Adjustment Account',
    status: 'Cleared',
    date: '2024-01-12',
  },
];

const financeColumns = [
  {
    key: 'id',
    label: 'Transaction',
    render: (value: string, row: any) => (
      <Box>
        <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
          {value}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {row.type} • {row.date}
        </Typography>
      </Box>
    ),
  },
  {
    key: 'account',
    label: 'Account',
  },
  {
    key: 'amount',
    label: 'Amount',
    render: (value: string, row: any) => (
      <Typography 
        variant="body2" 
        sx={{ 
          fontWeight: 600,
          color: row.type === 'Receipt' ? 'success.main' : 'error.main'
        }}
      >
        {row.type === 'Payment' ? '-' : '+'}{value}
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
        color={value === 'Cleared' ? 'success' : 'warning'}
        sx={{ fontSize: '0.75rem' }}
      />
    ),
  },
];

const MobileFinance: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredData = financeData.filter(item =>
    item.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.account.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const rightActions = (
    <MobileButton
      variant="contained"
      startIcon={<Add />}
      size="small"
    >
      New Entry
    </MobileButton>
  );

  return (
    <MobileDashboardLayout
      title="Finance"
      subtitle="Financial Management"
      rightActions={rightActions}
      showBottomNav={true}
    >
      {/* Search */}
      <MobileSearchBar
        value={searchQuery}
        onChange={setSearchQuery}
        placeholder="Search transactions..."
      />

      {/* Financial Summary */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                <TrendingUp sx={{ fontSize: '2rem', color: 'success.main' }} />
              </Box>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'success.main' }}>
                ₹2,84,750
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Income
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={6}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                <TrendingDown sx={{ fontSize: '2rem', color: 'error.main' }} />
              </Box>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'error.main' }}>
                ₹1,45,230
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Expenses
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={12}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                <AccountBalance sx={{ fontSize: '2rem', color: 'primary.main' }} />
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>
                ₹1,39,520
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Net Balance
              </Typography>
              <Typography variant="caption" sx={{ color: 'success.main', fontWeight: 600 }}>
                +12.5% from last month
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
      </Grid>

      {/* Recent Transactions */}
      <MobileCard title="Recent Transactions">
        <MobileTable
          columns={financeColumns}
          data={filteredData}
          onRowClick={(row) => console.log('Transaction clicked:', row)}
          showChevron={true}
          emptyMessage="No transactions found"
        />
      </MobileCard>

      {/* Quick Actions */}
      <MobileCard title="Quick Actions">
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <MobileButton 
              variant="outlined" 
              fullWidth
              startIcon={<TrendingUp />}
            >
              Receipt Entry
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton 
              variant="outlined" 
              fullWidth
              startIcon={<TrendingDown />}
            >
              Payment Entry
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              Bank Reconciliation
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              Financial Reports
            </MobileButton>
          </Grid>
        </Grid>
      </MobileCard>
    </MobileDashboardLayout>
  );
};

export default MobileFinance;