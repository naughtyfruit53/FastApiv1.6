// pages/marketing/campaigns.tsx
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
  Fab,
  LinearProgress
} from '@mui/material';
import { 
  Campaign, 
  Add, 
  Email,
  Sms,
  Groups,
  Schedule,
  CheckCircle,
  PlayArrow,
  Edit,
  Visibility,
  BarChart
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';
import { ProtectedPage } from '../../components/ProtectedPage';

const MarketingCampaignsPage: React.FC = () => {
  const campaignStats = {
    total: 24,
    active: 8,
    scheduled: 4,
    completed: 12
  };

  const campaigns = [
    { 
      id: 1,
      name: 'Summer Sale 2024', 
      type: 'email',
      status: 'active', 
      reach: 15000,
      opened: 4500,
      clicked: 675,
      budget: 5000,
      spent: 2300,
      startDate: '2024-06-01',
      endDate: '2024-06-30'
    },
    { 
      id: 2,
      name: 'Product Launch SMS', 
      type: 'sms',
      status: 'scheduled', 
      reach: 8000,
      opened: 0,
      clicked: 0,
      budget: 2000,
      spent: 0,
      startDate: '2024-07-01',
      endDate: '2024-07-07'
    },
    { 
      id: 3,
      name: 'Social Media Awareness', 
      type: 'social',
      status: 'active', 
      reach: 25000,
      opened: 12000,
      clicked: 1800,
      budget: 8000,
      spent: 6200,
      startDate: '2024-05-15',
      endDate: '2024-07-15'
    },
    { 
      id: 4,
      name: 'Customer Retention Email', 
      type: 'email',
      status: 'completed', 
      reach: 5000,
      opened: 2250,
      clicked: 450,
      budget: 1500,
      spent: 1500,
      startDate: '2024-04-01',
      endDate: '2024-04-15'
    },
  ];

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'email': return <Email />;
      case 'sms': return <Sms />;
      case 'social': return <Groups />;
      default: return <Campaign />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'scheduled': return 'warning';
      case 'completed': return 'primary';
      case 'paused': return 'error';
      default: return 'default';
    }
  };

  const calculateEngagementRate = (opened: number, reach: number) => {
    return reach > 0 ? Math.round((opened / reach) * 100) : 0;
  };

  const calculateClickThroughRate = (clicked: number, opened: number) => {
    return opened > 0 ? Math.round((clicked / opened) * 100) : 0;
  };

  return (
    <ProtectedPage moduleKey="marketing" action="read">
    <DashboardLayout
      title="Marketing Campaigns"
      subtitle="Create and manage your marketing campaigns"
      actions={
        <Button 
          variant="contained" 
          startIcon={<Add />}
        >
          New Campaign
        </Button>
      }
    >
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Alert severity="info" sx={{ mb: 3 }}>
            Track your marketing campaign performance across email, SMS, and social media channels.
          </Alert>
        </Grid>
        
        {/* Campaign Statistics */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Campaign sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Total Campaigns</Typography>
              </Box>
              <Typography variant="h3" color="primary.main">
                {campaignStats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <PlayArrow sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="h6">Active</Typography>
              </Box>
              <Typography variant="h3" color="success.main">
                {campaignStats.active}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Schedule sx={{ mr: 1, color: 'warning.main' }} />
                <Typography variant="h6">Scheduled</Typography>
              </Box>
              <Typography variant="h3" color="warning.main">
                {campaignStats.scheduled}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CheckCircle sx={{ mr: 1, color: 'info.main' }} />
                <Typography variant="h6">Completed</Typography>
              </Box>
              <Typography variant="h3" color="info.main">
                {campaignStats.completed}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Campaigns Table */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Campaign Performance
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Campaign</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Reach</TableCell>
                      <TableCell>Engagement</TableCell>
                      <TableCell>CTR</TableCell>
                      <TableCell>Budget</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {campaigns.map((campaign) => (
                      <TableRow key={campaign.id}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {campaign.name}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {campaign.startDate} - {campaign.endDate}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {getTypeIcon(campaign.type)}
                            <Typography variant="body2" sx={{ ml: 1, textTransform: 'capitalize' }}>
                              {campaign.type}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={campaign.status}
                            color={getStatusColor(campaign.status) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{campaign.reach.toLocaleString()}</TableCell>
                        <TableCell>
                          <Box>
                            <Typography variant="body2">
                              {calculateEngagementRate(campaign.opened, campaign.reach)}%
                            </Typography>
                            <LinearProgress 
                              variant="determinate" 
                              value={calculateEngagementRate(campaign.opened, campaign.reach)}
                              sx={{ width: 60, height: 4 }}
                            />
                          </Box>
                        </TableCell>
                        <TableCell>
                          {calculateClickThroughRate(campaign.clicked, campaign.opened)}%
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            ${campaign.spent.toLocaleString()} / ${campaign.budget.toLocaleString()}
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={(campaign.spent / campaign.budget) * 100}
                            sx={{ width: 80, height: 4 }}
                          />
                        </TableCell>
                        <TableCell align="right">
                          <IconButton size="small">
                            <Visibility />
                          </IconButton>
                          <IconButton size="small">
                            <Edit />
                          </IconButton>
                          <IconButton size="small">
                            <BarChart />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              
              <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                <Button variant="outlined" href="/marketing/campaigns/email">
                  Email Campaigns
                </Button>
                <Button variant="outlined" href="/marketing/campaigns/sms">
                  SMS Campaigns
                </Button>
                <Button variant="outlined" href="/marketing/campaigns/social">
                  Social Media
                </Button>
                <Button variant="outlined" href="/marketing/analytics">
                  Campaign Analytics
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
    </ProtectedPage>
  );
};

export default MarketingCampaignsPage;