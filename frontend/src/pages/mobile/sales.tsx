import React, { useState } from 'react';
import { Box, Grid, Typography, Chip, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import { Add, FilterList, TrendingUp, Person, Business, AddCircle, Assessment, Groups, Phone, Email, Event } from '@mui/icons-material';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton, 
  MobileTable,
  MobileSearchBar,
  MobilePullToRefresh,
  MobileBottomSheet,
  MobileContextualActions,
  createStandardActions 
} from '../../components/mobile';
import useSharedSales from '../../hooks/useSharedSales';
import ModernLoading from "../../components/ModernLoading";

// Define mobile-optimized table columns for sales leads
const leadsColumns = [
  {
    key: 'company_name',
    label: 'Lead',
    render: (value: string, row: any) => (
      <Box>
        <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
          {value}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {row.contact_person} • {row.source}
        </Typography>
      </Box>
    ),
  },
  {
    key: 'formatted_value',
    label: 'Value',
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
        label={value.charAt(0).toUpperCase() + value.slice(1)}
        size="small"
        color={
          value === 'won' ? 'success' 
          : value === 'qualified' || value === 'proposal' ? 'primary'
          : value === 'contacted' ? 'warning' 
          : value === 'lost' ? 'error'
          : 'default'
        }
        sx={{ fontSize: '0.75rem' }}
      />
    ),
  },
];

const MobileSales: React.FC = () => {
  const [localSearchQuery, setLocalSearchQuery] = useState('');
  const [quickActionsOpen, setQuickActionsOpen] = useState(false);
  
  // Use shared sales business logic
  const {
    metrics,
    filteredLeads,
    opportunities,
    customers,
    loading,
    error,
    refreshing,
    searchLeads,
    refresh,
  } = useSharedSales();

  // Handle search with local state and shared logic
  const handleSearch = (query: string) => {
    setLocalSearchQuery(query);
    searchLeads(query);
  };

  // Contextual actions for sales
  const contextualActions = createStandardActions.sales({
    onAddLead: () => setQuickActionsOpen(true),
    onFollowUp: () => console.log('Schedule follow-up'),
    onConvert: () => console.log('Convert lead'),
    onQuote: () => console.log('Create quote'),
  }).concat(
    createStandardActions.dataManagement({
      onRefresh: refresh,
      onFilter: () => console.log('Open filter'),
    })
  );

  const rightActions = (
    <MobileButton
      variant="contained"
      startIcon={<Add />}
      size="small"
      onClick={() => setQuickActionsOpen(true)}
    >
      Actions
    </MobileButton>
  );

  if (loading) {
    return (
      <MobileDashboardLayout
        title="Sales"
        subtitle="Manage leads and opportunities"
        rightActions={rightActions}
        showBottomNav={true}
      >
        <ModernLoading
          type="skeleton"
          skeletonType="dashboard"
          count={6}
          message="Loading sales data..."
        />
      </MobileDashboardLayout>
    );
  }

  if (error) {
    return (
      <MobileDashboardLayout
        title="Sales"
        subtitle="Manage leads and opportunities"
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
    );
  }

  return (
    <MobileDashboardLayout
      title="Sales"
      subtitle="Manage leads and opportunities"
      rightActions={rightActions}
      showBottomNav={true}
    >
      <MobilePullToRefresh
        onRefresh={refresh}
        isRefreshing={refreshing}
        enabled={true}
      >
        {/* Search and Filter */}
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <Box sx={{ flex: 1 }}>
            <MobileSearchBar
              value={localSearchQuery}
              onChange={handleSearch}
              placeholder="Search leads or companies..."
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

        {/* Sales Metrics - Using shared business logic */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={4}>
            <MobileCard>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                  <TrendingUp sx={{ fontSize: '1.5rem', color: 'success.main' }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'success.main' }}>
                  {metrics?.formatted_sales_this_month || '₹0'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Sales This Month
                </Typography>
                {metrics?.sales_trend && (
                  <Typography variant="caption" sx={{ display: 'block', color: 'success.main' }}>
                    +{metrics.sales_trend}%
                  </Typography>
                )}
              </Box>
            </MobileCard>
          </Grid>
          <Grid item xs={4}>
            <MobileCard>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                  <Person sx={{ fontSize: '1.5rem', color: 'primary.main' }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main' }}>
                  {metrics?.total_leads || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total Leads
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', color: 'primary.main' }}>
                  +{metrics?.leads_this_month || 0} this month
                </Typography>
              </Box>
            </MobileCard>
          </Grid>
          <Grid item xs={4}>
            <MobileCard>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                  <Business sx={{ fontSize: '1.5rem', color: 'warning.main' }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'warning.main' }}>
                  {metrics?.win_rate || 0}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Win Rate
                </Typography>
                <Typography variant="caption" sx={{ display: 'block' }}>
                  {metrics?.total_opportunities || 0} opportunities
                </Typography>
              </Box>
            </MobileCard>
          </Grid>
        </Grid>

        {/* Sales Target Progress */}
        {metrics && (
          <MobileCard title="Monthly Target">
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Progress</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {metrics.target_achievement}%
                </Typography>
              </Box>
              <Box sx={{ 
                width: '100%', 
                height: 8, 
                bgcolor: 'grey.200', 
                borderRadius: 1,
                overflow: 'hidden'
              }}>
                <Box sx={{ 
                  width: `${Math.min(metrics.target_achievement, 100)}%`, 
                  height: '100%',
                  bgcolor: metrics.target_achievement >= 100 ? 'success.main' : 'primary.main',
                  transition: 'width 0.3s ease-in-out'
                }} />
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  Achieved: {metrics.formatted_sales_this_month}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Target: {metrics.formatted_sales_target}
                </Typography>
              </Box>
            </Box>
          </MobileCard>
        )}

        {/* Recent Leads - Using shared data */}
        <MobileCard title="Recent Leads">
          <MobileTable
            columns={leadsColumns}
            data={filteredLeads}
            onRowClick={(row) => console.log('Lead clicked:', row)}
            showChevron={true}
            emptyMessage="No leads found"
          />
        </MobileCard>

        {/* Quick Actions */}
        <MobileCard title="Quick Actions">
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <MobileButton 
                variant="outlined" 
                fullWidth
                onClick={() => setQuickActionsOpen(true)}
                startIcon={<Add />}
              >
                Open Quick Actions Menu
              </MobileButton>
            </Grid>
          </Grid>
        </MobileCard>

        {/* TODO: Future implementations using shared business logic */}
        {/* TODO: Integrate with crmService.getSalesData() - now implemented via useSharedSales */}
        {/* TODO: Add lead management interface with swipeable cards */}
        {/* TODO: Implement mobile-optimized opportunity pipeline */}
        {/* TODO: Add customer analytics with touch-friendly charts */}
        {/* TODO: Implement commission tracking dashboard */}
        {/* TODO: Add advanced filtering and search capabilities - partially implemented */}
        {/* TODO: Implement export functionality for mobile (PDF, Excel sharing) */}
        {/* TODO: Add touch-optimized forms for lead/opportunity creation */}
        {/* TODO: Add pull-to-refresh for live data updates - now implemented */}
        {/* TODO: Implement offline data caching for mobile access */}
      </MobilePullToRefresh>
      
      {/* Quick Actions Bottom Sheet */}
      <MobileBottomSheet
        open={quickActionsOpen}
        onClose={() => setQuickActionsOpen(false)}
        title="Quick Actions"
        height="auto"
        showHandle={true}
        dismissible={true}
      >
        <List sx={{ py: 0 }}>
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('Create new lead');
            }}
            sx={{ 
              borderRadius: 2, 
              mb: 1,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <AddCircle color="primary" />
            </ListItemIcon>
            <ListItemText
              primary="Add New Lead"
              secondary="Create a new sales lead"
            />
          </ListItem>
          
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('Generate sales report');
            }}
            sx={{ 
              borderRadius: 2, 
              mb: 1,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <Assessment color="secondary" />
            </ListItemIcon>
            <ListItemText
              primary="Sales Report"
              secondary="Generate performance report"
            />
          </ListItem>
          
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('Schedule follow-up');
            }}
            sx={{ 
              borderRadius: 2, 
              mb: 1,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <Event color="warning" />
            </ListItemIcon>
            <ListItemText
              primary="Schedule Follow-up"
              secondary="Set reminder for lead follow-up"
            />
          </ListItem>
          
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('View customers');
            }}
            sx={{ 
              borderRadius: 2, 
              mb: 1,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <Groups color="info" />
            </ListItemIcon>
            <ListItemText
              primary="Customer List"
              secondary="Browse all customers"
            />
          </ListItem>
          
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('Make call');
            }}
            sx={{ 
              borderRadius: 2, 
              mb: 1,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <Phone color="success" />
            </ListItemIcon>
            <ListItemText
              primary="Quick Call"
              secondary="Call top priority lead"
            />
          </ListItem>
          
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('Send email');
            }}
            sx={{ 
              borderRadius: 2,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <Email color="error" />
            </ListItemIcon>
            <ListItemText
              primary="Send Email"
              secondary="Email campaign to leads"
            />
          </ListItem>
        </List>
      </MobileBottomSheet>

      {/* Contextual Actions */}
      <MobileContextualActions
        actions={contextualActions}
        primaryAction={{
          icon: <Add />,
          name: 'Add Lead',
          onClick: () => setQuickActionsOpen(true),
          color: 'primary'
        }}
      />
    </MobileDashboardLayout>
  );
};

export default MobileSales;