// frontend/src/pages/marketing/index.tsx

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Campaign as CampaignIcon,
  LocalOffer as LocalOfferIcon,
  TrendingUp as TrendingUpIcon,
  AttachMoney as AttachMoneyIcon,
  Email as EmailIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';
import { useAuth } from '@/context/AuthContext';
import { marketingService, Campaign, Promotion, MarketingAnalytics } from '../../services/marketingService';

const campaignStatusColors: Record<string, string> = {
  draft: 'default',
  scheduled: 'info',
  active: 'success',
  paused: 'warning',
  completed: 'primary',
  cancelled: 'error',
};

const campaignTypeIcons: Record<string, JSX.Element> = {
  email: <EmailIcon />,
  sms: <CampaignIcon />,
  social_media: <AnalyticsIcon />,
  digital_ads: <TrendingUpIcon />,
};

export default function MarketingDashboard() {
  const { user } = useAuth();
  const [currentTab, setCurrentTab] = useState(0);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [analytics, setAnalytics] = useState<MarketingAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [openCampaignDialog, setOpenCampaignDialog] = useState(false);
  const [openPromotionDialog, setOpenPromotionDialog] = useState(false);

  useEffect(() => {
    loadMarketingData();
  }, []);

  const loadMarketingData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [campaignsData, promotionsData, analyticsData] = await Promise.all([
        marketingService.getCampaigns(),
        marketingService.getPromotions(),
        marketingService.getAnalytics()
      ]);

      setCampaigns(campaignsData);
      setPromotions(promotionsData);
      setAnalytics(analyticsData);

    } catch (err: any) {
      console.error('Error loading marketing data:', err);
      setError(err.userMessage || 'Failed to load marketing data');
      
      // Fallback to empty data to prevent crashes
      setCampaigns([]);
      setPromotions([]);
      setAnalytics({
        total_campaigns: 0,
        active_campaigns: 0,
        total_promotions: 0,
        active_promotions: 0,
        campaign_roi: 0,
        promotion_redemption_rate: 0,
        email_open_rate: 0,
        click_through_rate: 0,
        conversion_rate: 0,
        customer_acquisition_cost: 0,
        lifetime_value: 0,
        revenue_from_campaigns: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  const filteredCampaigns = campaigns.filter(
    (campaign) =>
      campaign.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      campaign.campaign_number.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredPromotions = promotions.filter(
    (promotion) =>
      promotion.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      promotion.promotion_code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const renderAnalyticsCards = () => {
    if (!analytics) return null;

    return (
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CampaignIcon color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Campaigns
                  </Typography>
                  <Typography variant="h5" component="div">
                    {analytics?.total_campaigns || 0}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {analytics?.active_campaigns || 0} active
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <EmailIcon color="info" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Contacts
                  </Typography>
                  <Typography variant="h5" component="div">
                    {(analytics?.total_promotions || 0).toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {analytics?.email_open_rate || 0}% avg open rate
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <AttachMoneyIcon color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Marketing Revenue
                  </Typography>
                  <Typography variant="h5" component="div">
                    ${(analytics?.revenue_from_campaigns || 0).toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    ${(analytics?.customer_acquisition_cost || 0).toLocaleString()} spent
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUpIcon color="warning" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Marketing ROI
                  </Typography>
                  <Typography variant="h5" component="div">
                    {analytics?.campaign_roi || 0}%
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {analytics?.conversion_rate || 0}% conversion rate
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderCampaignsTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Campaign #</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Performance</TableCell>
            <TableCell>Budget</TableCell>
            <TableCell>Revenue</TableCell>
            <TableCell>ROI</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {filteredCampaigns.map((campaign) => {
            const openRate = campaign.delivered_count > 0 ? (campaign.opened_count / campaign.delivered_count) * 100 : 0;
            const conversionRate = campaign.delivered_count > 0 ? (campaign.converted_count / campaign.delivered_count) * 100 : 0;
            const roi = campaign.budget ? ((campaign.revenue_generated - campaign.budget) / campaign.budget) * 100 : 0;

            return (
              <TableRow key={campaign.id} hover>
                <TableCell>{campaign.campaign_number}</TableCell>
                <TableCell>{campaign.name}</TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {campaignTypeIcons[campaign.campaign_type] || <CampaignIcon />}
                    <Typography sx={{ ml: 1, textTransform: 'capitalize' }}>
                      {campaign.campaign_type.replace('_', ' ')}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={campaign.status}
                    color={campaignStatusColors[campaign.status] as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box sx={{ minWidth: 120 }}>
                    <Typography variant="body2">
                      {openRate.toFixed(1)}% open | {conversionRate.toFixed(1)}% conv
                    </Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={Math.min(openRate, 100)} 
                      sx={{ mt: 0.5 }}
                    />
                  </Box>
                </TableCell>
                <TableCell>
                  {campaign.budget ? `$${campaign.budget.toLocaleString()}` : '-'}
                </TableCell>
                <TableCell>${campaign.revenue_generated.toLocaleString()}</TableCell>
                <TableCell>
                  <Typography color={roi > 0 ? 'success.main' : 'error.main'}>
                    {roi.toFixed(1)}%
                  </Typography>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const renderPromotionsTable = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Code</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Discount</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Redemptions</TableCell>
            <TableCell>Total Discount</TableCell>
            <TableCell>Valid Until</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {filteredPromotions.map((promotion) => (
            <TableRow key={promotion.id} hover>
              <TableCell>
                <Typography variant="body2" component="code">
                  {promotion.promotion_code}
                </Typography>
              </TableCell>
              <TableCell>{promotion.name}</TableCell>
              <TableCell>
                <Typography sx={{ textTransform: 'capitalize' }}>
                  {promotion.promotion_type.replace('_', ' ')}
                </Typography>
              </TableCell>
              <TableCell>
                {promotion.discount_percentage 
                  ? `${promotion.discount_percentage}%` 
                  : `$${promotion.discount_amount}`}
              </TableCell>
              <TableCell>
                <Chip
                  label={promotion.is_active ? 'Active' : 'Inactive'}
                  color={promotion.is_active ? 'success' : 'default'}
                  size="small"
                />
              </TableCell>
              <TableCell>{promotion.total_redemptions}</TableCell>
              <TableCell>${promotion.total_discount_given.toLocaleString()}</TableCell>
              <TableCell>
                {promotion.valid_until 
                  ? new Date(promotion.valid_until).toLocaleDateString()
                  : 'No expiry'}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Marketing Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenCampaignDialog(true)}
          >
            Create Campaign
          </Button>
          <Button
            variant="outlined"
            startIcon={<LocalOfferIcon />}
            onClick={() => setOpenPromotionDialog(true)}
          >
            Add Promotion
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
          <Button size="small" onClick={loadMarketingData} sx={{ ml: 1 }}>
            Retry
          </Button>
        </Alert>
      )}

      {renderAnalyticsCards()}

      <Card>
        <CardContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
            <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
              <Tab label="Campaigns" />
              <Tab label="Promotions" />
            </Tabs>
          </Box>

          <Box sx={{ mb: 2 }}>
            <TextField
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ maxWidth: 300 }}
            />
          </Box>

          {currentTab === 0 && renderCampaignsTable()}
          {currentTab === 1 && renderPromotionsTable()}
        </CardContent>
      </Card>

      {/* Create Campaign Dialog - Placeholder */}
      <Dialog
        open={openCampaignDialog}
        onClose={() => setOpenCampaignDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create New Campaign</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  label="Campaign Name"
                  fullWidth
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Campaign Type</InputLabel>
                  <Select defaultValue="email">
                    <MenuItem value="email">Email</MenuItem>
                    <MenuItem value="sms">SMS</MenuItem>
                    <MenuItem value="social_media">Social Media</MenuItem>
                    <MenuItem value="digital_ads">Digital Ads</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Budget"
                  type="number"
                  fullWidth
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Start Date"
                  type="date"
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="End Date"
                  type="date"
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Description"
                  multiline
                  rows={3}
                  fullWidth
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCampaignDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setOpenCampaignDialog(false)}>
            Create Campaign
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Promotion Dialog - Placeholder */}
      <Dialog
        open={openPromotionDialog}
        onClose={() => setOpenPromotionDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Add New Promotion</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Promotion Code"
                  fullWidth
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Promotion Name"
                  fullWidth
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Promotion Type</InputLabel>
                  <Select defaultValue="percentage_discount">
                    <MenuItem value="percentage_discount">Percentage Discount</MenuItem>
                    <MenuItem value="fixed_amount_discount">Fixed Amount Discount</MenuItem>
                    <MenuItem value="buy_x_get_y">Buy X Get Y</MenuItem>
                    <MenuItem value="free_shipping">Free Shipping</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Discount Value"
                  type="number"
                  fullWidth
                  helperText="Percentage or fixed amount"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Valid From"
                  type="date"
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Valid Until"
                  type="date"
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenPromotionDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setOpenPromotionDialog(false)}>
            Create Promotion
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}