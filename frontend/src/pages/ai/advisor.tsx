// AI Business Advisor Page
import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  LinearProgress,
  Alert,
  AlertTitle,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Inventory as InventoryIcon,
  AttachMoney as MoneyIcon,
  People as PeopleIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Info as InfoIcon,
  ArrowUpward as ArrowUpIcon,
  ArrowDownward as ArrowDownIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { ProtectedPage } from '../../components/ProtectedPage';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`advisor-tabpanel-${index}`}
      aria-labelledby={`advisor-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AIBusinessAdvisorPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);

  const categories = [
    { id: 'inventory', label: 'Inventory', icon: <InventoryIcon /> },
    { id: 'cash_flow', label: 'Cash Flow', icon: <MoneyIcon /> },
    { id: 'sales', label: 'Sales', icon: <TrendingUpIcon /> },
    { id: 'customer_retention', label: 'Customer Retention', icon: <PeopleIcon /> },
  ];

  const mockRecommendations = {
    inventory: [
      {
        title: 'Reorder Low Stock Items',
        description: '5 items are below minimum stock level',
        priority: 'high',
        impact: 'High risk of stockouts',
        action: 'Review and place orders',
        metrics: { items: 5, value: '₹45,000' },
      },
      {
        title: 'Reduce Overstock',
        description: '3 items have excess inventory',
        priority: 'medium',
        impact: 'Capital tied up in excess inventory',
        action: 'Promote or discount items',
        metrics: { items: 3, value: '₹28,000' },
      },
    ],
    cash_flow: [
      {
        title: 'Collect Outstanding Payments',
        description: '₹1,25,000 in overdue invoices',
        priority: 'high',
        impact: 'Cash flow constraint',
        action: 'Send payment reminders',
        metrics: { invoices: 8, amount: '₹1,25,000' },
      },
      {
        title: 'Optimize Payment Terms',
        description: 'Negotiate better payment terms with suppliers',
        priority: 'medium',
        impact: 'Improved working capital',
        action: 'Review vendor contracts',
        metrics: { vendors: 12, savings: '₹15,000/month' },
      },
    ],
    sales: [
      {
        title: 'Capitalize on Seasonal Trends',
        description: 'Sales increase expected next month',
        priority: 'medium',
        impact: 'Revenue growth opportunity',
        action: 'Increase marketing spend',
        metrics: { growth: '+15%', revenue: '₹2,50,000' },
      },
      {
        title: 'Focus on High-Margin Products',
        description: 'Top 3 products drive 60% of profit',
        priority: 'low',
        impact: 'Maximize profitability',
        action: 'Optimize product mix',
        metrics: { products: 3, margin: '45%' },
      },
    ],
    customer_retention: [
      {
        title: 'Re-engage Inactive Customers',
        description: '15 customers haven\'t purchased in 90+ days',
        priority: 'high',
        impact: 'Potential revenue loss',
        action: 'Launch win-back campaign',
        metrics: { customers: 15, value: '₹1,80,000' },
      },
      {
        title: 'Reward Loyal Customers',
        description: 'Top 10 customers generate 40% of revenue',
        priority: 'medium',
        impact: 'Strengthen relationships',
        action: 'Create loyalty program',
        metrics: { customers: 10, revenue: '₹5,00,000' },
      },
    ],
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <WarningIcon />;
      case 'medium':
        return <InfoIcon />;
      case 'low':
        return <CheckIcon />;
      default:
        return <InfoIcon />;
    }
  };

  return (
    <ProtectedPage moduleKey="ai" action="read">
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          AI Business Advisor
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Get AI-powered recommendations to optimize your business operations
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <WarningIcon color="error" sx={{ mr: 1 }} />
                <Typography variant="h6" color="error">
                  3
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                High Priority
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <InfoIcon color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6" color="warning.main">
                  4
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Medium Priority
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUpIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6" color="success.main">
                  ₹5.2L
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Potential Impact
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckIcon color="info" sx={{ mr: 1 }} />
                <Typography variant="h6" color="info.main">
                  92%
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Confidence Score
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          {categories.map((category, index) => (
            <Tab
              key={category.id}
              label={category.label}
              icon={category.icon}
              iconPosition="start"
            />
          ))}
        </Tabs>
      </Paper>

      {/* Tab Panels */}
      {categories.map((category, index) => (
        <TabPanel value={activeTab} index={index} key={category.id}>
          <Grid container spacing={3}>
            {mockRecommendations[category.id as keyof typeof mockRecommendations].map(
              (recommendation, idx) => (
                <Grid item xs={12} key={idx}>
                  <Card>
                    <CardContent>
                      <Box
                        sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'flex-start',
                          mb: 2,
                        }}
                      >
                        <Box sx={{ flex: 1 }}>
                          <Box
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                              mb: 1,
                            }}
                          >
                            <Typography variant="h6" fontWeight="bold">
                              {recommendation.title}
                            </Typography>
                            <Chip
                              label={recommendation.priority.toUpperCase()}
                              color={getPriorityColor(recommendation.priority)}
                              size="small"
                              sx={{ ml: 2 }}
                              icon={getPriorityIcon(recommendation.priority)}
                            />
                          </Box>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            gutterBottom
                          >
                            {recommendation.description}
                          </Typography>
                        </Box>
                      </Box>

                      <Divider sx={{ my: 2 }} />

                      <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                          <Alert severity="info" icon={<InfoIcon />}>
                            <AlertTitle>Impact</AlertTitle>
                            {recommendation.impact}
                          </Alert>
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <Alert severity="success" icon={<CheckIcon />}>
                            <AlertTitle>Recommended Action</AlertTitle>
                            {recommendation.action}
                          </Alert>
                        </Grid>
                      </Grid>

                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Key Metrics:
                        </Typography>
                        <Grid container spacing={1}>
                          {Object.entries(recommendation.metrics).map(
                            ([key, value]) => (
                              <Grid item key={key}>
                                <Chip
                                  label={`${key}: ${value}`}
                                  size="small"
                                  variant="outlined"
                                />
                              </Grid>
                            )
                          )}
                        </Grid>
                      </Box>

                      <Box sx={{ mt: 3 }}>
                        <Button variant="contained" color="primary" sx={{ mr: 1 }}>
                          Take Action
                        </Button>
                        <Button variant="outlined">View Details</Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              )
            )}
          </Grid>
        </TabPanel>
      ))}

      {/* Info Box */}
      <Paper sx={{ p: 3, mt: 4, backgroundColor: '#f5f5f5' }}>
        <Typography variant="h6" gutterBottom fontWeight="bold">
          How AI Recommendations Work
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Our AI Business Advisor analyzes your historical data, market trends, and
          industry benchmarks to provide personalized recommendations. The system
          continuously learns from your business patterns to improve accuracy over time.
        </Typography>
        <List dense>
          <ListItem>
            <ListItemIcon>
              <CheckIcon color="success" />
            </ListItemIcon>
            <ListItemText
              primary="Real-time data analysis"
              secondary="Recommendations update as your business data changes"
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <CheckIcon color="success" />
            </ListItemIcon>
            <ListItemText
              primary="Priority scoring"
              secondary="Focus on high-impact actions first"
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <CheckIcon color="success" />
            </ListItemIcon>
            <ListItemText
              primary="Actionable insights"
              secondary="Clear next steps with measurable outcomes"
            />
          </ListItem>
        </List>
      </Paper>
    </Container>
    </ProtectedPage>
  );
};

export default AIBusinessAdvisorPage;
