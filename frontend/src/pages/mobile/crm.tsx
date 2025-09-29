import React, { useState } from 'react';
import { Box, Grid, Typography, Avatar, Chip } from '@mui/material';
import { Add, Call, Email, Person, Business, TrendingUp } from '@mui/icons-material';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton, 
  MobileTable,
  MobileSearchBar 
} from '../../components/mobile';
import useSharedCRM from '../../hooks/useSharedCRM';
import ModernLoading from "../../components/ModernLoading";

// Define mobile-optimized table columns for CRM contacts
const crmColumns = [
  {
    key: 'name',
    label: 'Contact',
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
            {row.company || row.position}
          </Typography>
        </Box>
      </Box>
    ),
  },
  {
    key: 'email',
    label: 'Contact Info',
    render: (value: string, row: any) => (
      <Box>
        <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>{value}</Typography>
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
        label={value.charAt(0).toUpperCase() + value.slice(1)}
        size="small"
        color={
          value === 'customer' ? 'success' 
          : value === 'prospect' ? 'primary' 
          : value === 'active' ? 'info'
          : 'default'
        }
        sx={{ fontSize: '0.75rem' }}
      />
    ),
  },
];

const MobileCRM: React.FC = () => {
  // Use shared CRM business logic
  const {
    analytics,
    filteredContacts,
    interactions,
    segments,
    loading,
    error,
    refreshing,
    searchContacts,
    refresh,
    getContactStatuses,
  } = useSharedCRM();

  const [localSearchQuery, setLocalSearchQuery] = useState('');

  // Handle search with local state and shared logic
  const handleSearch = (query: string) => {
    setLocalSearchQuery(query);
    searchContacts(query);
  };

  const rightActions = (
    <MobileButton
      variant="contained"
      startIcon={<Add />}
      size="small"
    >
      Add Contact
    </MobileButton>
  );

  if (loading) {
    return (
      <MobileDashboardLayout
        title="CRM"
        subtitle="Customer Relationship Management"
        rightActions={rightActions}
        showBottomNav={true}
      >
        <ModernLoading
          type="skeleton"
          skeletonType="dashboard"
          count={6}
          message="Loading CRM data..."
        />
      </MobileDashboardLayout>
    );
  }

  if (error) {
    return (
      <MobileDashboardLayout
        title="CRM"
        subtitle="Customer Relationship Management"
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
      title="CRM"
      subtitle="Customer Relationship Management"
      rightActions={rightActions}
      showBottomNav={true}
    >
      {/* Search */}
      <MobileSearchBar
        value={localSearchQuery}
        onChange={handleSearch}
        placeholder="Search contacts, companies..."
      />

      {/* CRM Analytics - Using shared business logic */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={4}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                <Person sx={{ fontSize: '1.8rem', color: 'success.main' }} />
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 700, color: 'success.main' }}>
                {analytics?.active_customers || 0}
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
              <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                <Business sx={{ fontSize: '1.8rem', color: 'primary.main' }} />
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main' }}>
                {analytics?.prospects || 0}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Prospects
              </Typography>
              <Typography variant="caption" sx={{ display: 'block', color: 'primary.main' }}>
                +{analytics?.contacts_this_month || 0} this month
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={4}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                <TrendingUp sx={{ fontSize: '1.8rem', color: 'warning.main' }} />
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 700, color: 'warning.main' }}>
                {analytics?.conversion_rate || 0}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Conversion Rate
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
      </Grid>

      {/* Key Metrics */}
      {analytics && (
        <MobileCard title="Key Metrics">
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Box sx={{ textAlign: 'center', p: 1 }}>
                <Typography variant="h5" sx={{ fontWeight: 700, color: 'info.main' }}>
                  {analytics.total_interactions}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total Interactions
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', fontSize: '0.7rem' }}>
                  {analytics.interactions_this_week} this week
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box sx={{ textAlign: 'center', p: 1 }}>
                <Typography variant="h5" sx={{ fontWeight: 700, color: 'secondary.main' }}>
                  {analytics.avg_response_time_hours}h
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Avg Response Time
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ textAlign: 'center', p: 1 }}>
                <Typography variant="h5" sx={{ fontWeight: 700, color: 'success.main' }}>
                  {analytics.formatted_customer_lifetime_value}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Customer Lifetime Value
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </MobileCard>
      )}

      {/* Recent Contacts - Using shared data */}
      <MobileCard title="Recent Contacts">
        <MobileTable
          columns={crmColumns}
          data={filteredContacts}
          onRowClick={(row) => console.log('Contact clicked:', row)}
          showChevron={true}
          emptyMessage="No contacts found"
        />
      </MobileCard>

      {/* Top Lead Sources */}
      {analytics && analytics.top_sources && (
        <MobileCard title="Top Lead Sources">
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {analytics.top_sources.slice(0, 3).map((source, index) => (
              <Box key={source.source} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                  {source.source.replace('_', ' ')}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {source.count}
                  </Typography>
                  <Chip 
                    label={`${source.percentage}%`} 
                    size="small" 
                    variant="outlined"
                    sx={{ fontSize: '0.7rem', height: 20 }}
                  />
                </Box>
              </Box>
            ))}
          </Box>
        </MobileCard>
      )}

      {/* Quick Actions */}
      <MobileCard title="Quick Actions">
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <MobileButton 
              variant="outlined" 
              fullWidth
              startIcon={<Call />}
            >
              Log Call
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
              Add Meeting
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              CRM Report
            </MobileButton>
          </Grid>
        </Grid>
      </MobileCard>

      {/* TODO: Future implementations using shared business logic */}
      {/* TODO: Integrate with crmService - now implemented via useSharedCRM */}
      {/* TODO: Add customer detail view with interaction history */}
      {/* TODO: Implement lead conversion workflow with mobile forms */}
      {/* TODO: Add mobile-optimized pipeline with swipeable stages */}
      {/* TODO: Implement activity timeline with touch interactions */}
      {/* TODO: Add communication tracking (calls, emails, meetings) - partially implemented */}
      {/* TODO: Implement deal forecasting with mobile-friendly charts */}
      {/* TODO: Add contact import/export functionality */}
      {/* TODO: Implement customer segmentation and tagging - data available via segments */}
      {/* TODO: Add customer interaction history timeline - data available via interactions */}
      {/* TODO: Create mobile-optimized lead scoring interface */}
    </MobileDashboardLayout>
  );
};

export default MobileCRM;