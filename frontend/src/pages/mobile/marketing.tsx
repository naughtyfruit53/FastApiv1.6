import React, { useState } from 'react';
import { Box, Grid, Typography, Chip, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import { 
  Campaign, 
  Email, 
  Sms, 
  TrendingUp, 
  People, 
  Visibility, 
  Add,
  Analytics,
  Schedule,
  LocalOffer,
  Share
} from '@mui/icons-material';
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
import { useMobileDetection } from '../../hooks/useMobileDetection';
import ModernLoading from "../../components/ModernLoading";

// Mock data - TODO: Replace with real API integration
const mockCampaigns = [
  {
    id: 1,
    name: 'Summer Sale 2024',
    type: 'Email',
    status: 'active',
    sent: 1250,
    opened: 425,
    clicked: 85,
    conversion_rate: 6.8,
    created_date: '2024-01-15'
  },
  {
    id: 2,
    name: 'New Product Launch',
    type: 'SMS',
    status: 'draft',
    sent: 0,
    opened: 0,
    clicked: 0,
    conversion_rate: 0,
    created_date: '2024-01-20'
  },
  {
    id: 3,
    name: 'Customer Feedback',
    type: 'Email',
    status: 'completed',
    sent: 800,
    opened: 520,
    clicked: 156,
    conversion_rate: 19.5,
    created_date: '2024-01-10'
  }
];

const mockMetrics = {
  total_campaigns: 12,
  active_campaigns: 3,
  total_subscribers: 5420,
  avg_open_rate: 34.2,
  avg_click_rate: 8.7,
  monthly_growth: 12.5
};

// Define mobile-optimized table columns for campaigns
const campaignColumns = [
  {
    key: 'name',
    label: 'Campaign',
    render: (value: string, row: any) => (
      <Box>
        <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
          {value}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {row.type} • {row.created_date}
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
          value === 'active' ? 'success' 
          : value === 'completed' ? 'primary'
          : value === 'draft' ? 'warning' 
          : 'default'
        }
        sx={{ fontSize: '0.75rem' }}
      />
    ),
  },
  {
    key: 'conversion_rate',
    label: 'Conv. Rate',
    render: (value: number) => (
      <Typography variant="body2" sx={{ fontWeight: 600, color: 'success.main' }}>
        {value}%
      </Typography>
    ),
  },
];

const MobileMarketing: React.FC = () => {
  const [localSearchQuery, setLocalSearchQuery] = useState('');
  const [quickActionsOpen, setQuickActionsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const { isMobile } = useMobileDetection();

  const handleRefresh = async () => {
    setRefreshing(true);
    // TODO: Implement real refresh logic
    await new Promise(resolve => setTimeout(resolve, 1000));
    setRefreshing(false);
  };

  const handleSearch = (query: string) => {
    setLocalSearchQuery(query);
    // TODO: Implement real search logic
  };

  // Contextual actions for marketing
  const contextualActions = createStandardActions.crud({
    onCreate: () => setQuickActionsOpen(true),
  }).concat([
    {
      icon: <Analytics />,
      name: 'Analytics',
      onClick: () => console.log('View analytics'),
      color: 'info' as const
    },
    {
      icon: <Schedule />,
      name: 'Schedule',
      onClick: () => console.log('Schedule campaign'),
      color: 'warning' as const
    }
  ]);

  const rightActions = (
    <MobileButton
      variant="contained"
      startIcon={<Add />}
      size="small"
      onClick={() => setQuickActionsOpen(true)}
    >
      Campaign
    </MobileButton>
  );

  if (loading) {
    return (
      <MobileDashboardLayout
        title="Marketing"
        subtitle="Campaigns and analytics"
        rightActions={rightActions}
        showBottomNav={true}
      >
        <ModernLoading
          type="skeleton"
          skeletonType="dashboard"
          count={6}
          message="Loading marketing data..."
        />
      </MobileDashboardLayout>
    );
  }

  return (
    <MobileDashboardLayout
      title="Marketing"
      subtitle="Campaigns and analytics"
      rightActions={rightActions}
      showBottomNav={true}
    >
      <MobilePullToRefresh
        onRefresh={handleRefresh}
        isRefreshing={refreshing}
        enabled={true}
      >
        {/* Search and Filter */}
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <Box sx={{ flex: 1 }}>
            <MobileSearchBar
              value={localSearchQuery}
              onChange={handleSearch}
              placeholder="Search campaigns..."
            />
          </Box>
        </Box>

        {/* Marketing Metrics */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={4}>
            <MobileCard>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                  <Campaign sx={{ fontSize: '1.5rem', color: 'primary.main' }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main' }}>
                  {mockMetrics.total_campaigns}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total Campaigns
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', color: 'success.main' }}>
                  +{mockMetrics.active_campaigns} active
                </Typography>
              </Box>
            </MobileCard>
          </Grid>
          <Grid item xs={4}>
            <MobileCard>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                  <People sx={{ fontSize: '1.5rem', color: 'secondary.main' }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'secondary.main' }}>
                  {mockMetrics.total_subscribers.toLocaleString()}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Subscribers
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', color: 'success.main' }}>
                  +{mockMetrics.monthly_growth}% growth
                </Typography>
              </Box>
            </MobileCard>
          </Grid>
          <Grid item xs={4}>
            <MobileCard>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                  <TrendingUp sx={{ fontSize: '1.5rem', color: 'success.main' }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'success.main' }}>
                  {mockMetrics.avg_open_rate}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Open Rate
                </Typography>
                <Typography variant="caption" sx={{ display: 'block' }}>
                  {mockMetrics.avg_click_rate}% click rate
                </Typography>
              </Box>
            </MobileCard>
          </Grid>
        </Grid>

        {/* Campaign Performance Overview */}
        <MobileCard title="Performance Overview">
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Box sx={{ textAlign: 'center', p: 2, borderRadius: 2, bgcolor: 'action.hover' }}>
                <Visibility sx={{ fontSize: '2rem', color: 'info.main', mb: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'info.main' }}>
                  {mockMetrics.avg_open_rate}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Average Open Rate
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box sx={{ textAlign: 'center', p: 2, borderRadius: 2, bgcolor: 'action.hover' }}>
                <Analytics sx={{ fontSize: '2rem', color: 'warning.main', mb: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'warning.main' }}>
                  {mockMetrics.avg_click_rate}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Average Click Rate
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </MobileCard>

        {/* Recent Campaigns */}
        <MobileCard title="Recent Campaigns">
          <MobileTable
            columns={campaignColumns}
            data={mockCampaigns}
            onRowClick={(row) => console.log('Campaign clicked:', row)}
            showChevron={true}
            emptyMessage="No campaigns found"
          />
        </MobileCard>

        {/* Quick Actions */}
        <MobileCard title="Quick Actions">
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <MobileButton 
                variant="outlined" 
                fullWidth
                startIcon={<Email />}
                onClick={() => console.log('Create email campaign')}
              >
                Email Campaign
              </MobileButton>
            </Grid>
            <Grid item xs={6}>
              <MobileButton 
                variant="outlined" 
                fullWidth
                startIcon={<Sms />}
                onClick={() => console.log('Create SMS campaign')}
              >
                SMS Campaign
              </MobileButton>
            </Grid>
            <Grid item xs={6}>
              <MobileButton 
                variant="outlined" 
                fullWidth
                startIcon={<Analytics />}
                onClick={() => console.log('View analytics')}
              >
                Analytics
              </MobileButton>
            </Grid>
            <Grid item xs={6}>
              <MobileButton 
                variant="outlined" 
                fullWidth
                startIcon={<People />}
                onClick={() => console.log('Manage subscribers')}
              >
                Subscribers
              </MobileButton>
            </Grid>
          </Grid>
        </MobileCard>

        {/* TODO: Future implementations */}
        {/* TODO: Integrate with marketingService APIs */}
        {/* TODO: Add campaign builder interface */}
        {/* TODO: Implement mobile-optimized email template editor */}
        {/* TODO: Add campaign performance charts */}
        {/* TODO: Implement subscriber management */}
        {/* TODO: Add A/B testing functionality */}
        {/* TODO: Implement campaign scheduling */}
        {/* TODO: Add mobile push notification campaigns */}
        {/* TODO: Implement segmentation tools */}
        {/* TODO: Add social media integration */}
      </MobilePullToRefresh>
      
      {/* Quick Actions Bottom Sheet */}
      <MobileBottomSheet
        open={quickActionsOpen}
        onClose={() => setQuickActionsOpen(false)}
        title="Create Campaign"
        height="auto"
        showHandle={true}
        dismissible={true}
      >
        <List sx={{ py: 0 }}>
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('Create email campaign');
            }}
            sx={{ 
              borderRadius: 2, 
              mb: 1,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <Email color="primary" />
            </ListItemIcon>
            <ListItemText
              primary="Email Campaign"
              secondary="Send targeted email to subscribers"
            />
          </ListItem>
          
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('Create SMS campaign');
            }}
            sx={{ 
              borderRadius: 2, 
              mb: 1,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <Sms color="secondary" />
            </ListItemIcon>
            <ListItemText
              primary="SMS Campaign"
              secondary="Send SMS to customer list"
            />
          </ListItem>
          
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('Create social campaign');
            }}
            sx={{ 
              borderRadius: 2, 
              mb: 1,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <Share color="info" />
            </ListItemIcon>
            <ListItemText
              primary="Social Campaign"
              secondary="Schedule social media posts"
            />
          </ListItem>
          
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('Create promotion');
            }}
            sx={{ 
              borderRadius: 2,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <LocalOffer color="warning" />
            </ListItemIcon>
            <ListItemText
              primary="Promotion"
              secondary="Create discount or offer"
            />
          </ListItem>
        </List>
      </MobileBottomSheet>

      {/* Contextual Actions */}
      <MobileContextualActions
        actions={contextualActions}
        primaryAction={{
          icon: <Add />,
          name: 'New Campaign',
          onClick: () => setQuickActionsOpen(true),
          color: 'primary'
        }}
      />
    </MobileDashboardLayout>
  );
};

export default MobileMarketing;