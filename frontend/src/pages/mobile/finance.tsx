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
import useSharedFinance from '../../hooks/useSharedFinance';
import ModernLoading from "../../components/ModernLoading";
import { MobileNavProvider } from '../../context/MobileNavContext';

// Define mobile-optimized table columns for financial transactions
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
    key: 'formatted_amount',
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
  // Use shared finance business logic
  const {
    summary,
    filteredTransactions,
    loading,
    error,
    refreshing,
    filters,
    searchTransactions,
    refresh,
  } = useSharedFinance();

  const [localSearchQuery, setLocalSearchQuery] = useState('');

  // Handle search with debouncing
  const handleSearch = (query: string) => {
    setLocalSearchQuery(query);
    searchTransactions(query);
  };

  const rightActions = (
    <MobileButton
      variant="contained"
      startIcon={<Add />}
      size="small"
    >
      New Entry
    </MobileButton>
  );

  if (loading) {
    return (
      <MobileNavProvider>
        <MobileDashboardLayout
          title="Finance"
          subtitle="Financial Management"
          rightActions={rightActions}
          showBottomNav={true}
        >
          <ModernLoading
            type="skeleton"
            skeletonType="dashboard"
            count={6}
            message="Loading financial data..."
          />
        </MobileDashboardLayout>
      </MobileNavProvider>
    );
  }

  if (error) {
    return (
      <MobileNavProvider>
        <MobileDashboardLayout
          title="Finance"
          subtitle="Financial Management"
          rightActions={rightActions}
          showBottomNav={true}
        >
          <Box sx={{ p: 2 }}>
            <Typography color="error" variant="body1">
              Error: {error}
            </Typography>
            <MobileButton 
              variant="outlined" 
              onClick={refresh}
              disabled={refreshing}
              sx={{ mt: 2 }}
            >
              {refreshing ? 'Retrying...' : 'Retry'}
            </MobileButton>
          </Box>
        </MobileDashboardLayout>
      </MobileNavProvider>
    );
  }

  return (
    <MobileNavProvider>
      <MobileDashboardLayout
        title="Finance"
        subtitle="Financial Management"
        rightActions={rightActions}
        showBottomNav={true}
      >
      {/* Search */}
      <MobileSearchBar
        value={localSearchQuery}
        onChange={handleSearch}
        placeholder="Search transactions..."
      />

      {/* Financial Summary - Using shared business logic */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                <TrendingUp sx={{ fontSize: '2rem', color: 'success.main' }} />
              </Box>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'success.main' }}>
                {summary ? `₹${summary.total_income.toLocaleString()}` : '₹0'}
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
                {summary ? `₹${summary.total_expenses.toLocaleString()}` : '₹0'}
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
                {summary ? `₹${summary.net_balance.toLocaleString()}` : '₹0'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Net Balance
              </Typography>
              {summary && summary.monthly_trend > 0 && (
                <Typography variant="caption" sx={{ color: 'success.main', fontWeight: 600 }}>
                  +{summary.monthly_trend}% from last month
                </Typography>
              )}
            </Box>
          </MobileCard>
        </Grid>
      </Grid>

      {/* Recent Transactions - Using shared data */}
      <MobileCard title="Recent Transactions">
        <MobileTable
          columns={financeColumns}
          data={filteredTransactions}
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

      {/* TODO: Future implementations */}
      {/* TODO: Integrate with financial services (accounts payable, receivable, ledger) */}
      {/* TODO: Add real-time financial dashboard with live metrics */}
      {/* TODO: Implement mobile-optimized accounts payable interface */}
      {/* TODO: Add accounts receivable with customer payment tracking */}
      {/* TODO: Create touch-friendly financial report viewers (P&L, Balance Sheet, Cash Flow) */}
      {/* TODO: Implement mobile expense entry and tracking */}
      {/* TODO: Add quick payment recording interface with barcode scanning */}
      {/* TODO: Create mobile-optimized charts for financial KPIs */}
      {/* TODO: Add bank reconciliation mobile workflow */}
      {/* TODO: Implement budget tracking with mobile alerts and notifications */}
      {/* TODO: Add financial analytics with drill-down capabilities */}
      {/* TODO: Implement offline financial data caching */}
      {/* TODO: Add export functionality (PDF, Excel) for mobile sharing */}
    </MobileDashboardLayout>
    </MobileNavProvider>
  );
};

export default MobileFinance;