import React, { useState } from 'react';
import { Box, Grid, Typography, Paper } from '@mui/material';
import { BarChart, PieChart, TrendingUp, Assessment, DateRange } from '@mui/icons-material';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton,
  MobileSearchBar 
} from '../../components/mobile';

// TODO: CRITICAL - Replace hardcoded data with real reporting API integration
// TODO: Integrate with reporting services and analytics APIs across all modules
// TODO: Implement mobile-optimized report viewing interface with zoom and scroll
// TODO: Add interactive chart components optimized for touch interactions
// TODO: Create mobile export functionality (PDF, Excel) with native sharing
// TODO: Implement report scheduling with mobile notifications and delivery
// TODO: Add dashboard customization with drag-drop widgets for mobile
// TODO: Create drill-down analytics with touch navigation and data exploration
// TODO: Implement offline report caching for mobile access without connectivity
// TODO: Add mobile-specific KPI widgets and summary dashboards
// TODO: Create report sharing functionality via mobile apps and social platforms
// TODO: Implement real-time data refresh and live reporting updates
// TODO: Add advanced filtering and search capabilities for report data
// TODO: Create mobile report templates and customization tools
// TODO: Implement cross-module reporting with unified data views

// Sample report data - REPLACE WITH REAL API INTEGRATION
const reportCategories = [
  {
    title: 'Sales Reports',
    icon: <TrendingUp />,
    color: 'success.main',
    reports: [
      'Daily Sales Summary',
      'Monthly Sales Analysis',
      'Customer-wise Sales',
      'Product Performance',
    ],
  },
  {
    title: 'Financial Reports',
    icon: <Assessment />,
    color: 'primary.main',
    reports: [
      'Profit & Loss Statement',
      'Balance Sheet',
      'Cash Flow Statement',
      'Trial Balance',
    ],
  },
  {
    title: 'Inventory Reports',
    icon: <BarChart />,
    color: 'warning.main',
    reports: [
      'Stock Movement Report',
      'Low Stock Alert',
      'Valuation Report',
      'ABC Analysis',
    ],
  },
  {
    title: 'Customer Reports',
    icon: <PieChart />,
    color: 'info.main',
    reports: [
      'Customer Analysis',
      'Aging Report',
      'Payment Collection',
      'Customer Satisfaction',
    ],
  },
];

const quickMetrics = [
  {
    title: 'Reports Generated',
    value: '145',
    subtitle: 'This month',
    change: '+23%',
    changeType: 'positive' as const,
  },
  {
    title: 'Scheduled Reports',
    value: '8',
    subtitle: 'Active schedules',
    change: '+2',
    changeType: 'positive' as const,
  },
  {
    title: 'Export Downloads',
    value: '67',
    subtitle: 'Last 7 days',
    change: '+15%',
    changeType: 'positive' as const,
  },
];

const MobileReports: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredCategories = reportCategories.filter(category =>
    category.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    category.reports.some(report => 
      report.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  const rightActions = (
    <MobileButton
      variant="contained"
      startIcon={<DateRange />}
      size="small"
    >
      Schedule
    </MobileButton>
  );

  return (
    <MobileDashboardLayout
      title="Reports"
      subtitle="Analytics & Reporting"
      rightActions={rightActions}
      showBottomNav={true}
    >
      {/* Search */}
      <MobileSearchBar
        value={searchQuery}
        onChange={setSearchQuery}
        placeholder="Search reports..."
      />

      {/* Quick Metrics */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {quickMetrics.map((metric, index) => (
          <Grid item xs={4} key={index}>
            <MobileCard>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main' }}>
                  {metric.value}
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                  {metric.title}
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', fontSize: '0.7rem' }}>
                  {metric.subtitle}
                </Typography>
                <Typography variant="caption" sx={{ 
                  color: metric.changeType === 'positive' ? 'success.main' : 'error.main',
                  fontWeight: 600,
                  fontSize: '0.7rem',
                }}>
                  {metric.change}
                </Typography>
              </Box>
            </MobileCard>
          </Grid>
        ))}
      </Grid>

      {/* Report Categories */}
      {filteredCategories.map((category, index) => (
        <MobileCard 
          key={index}
          title={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ color: category.color }}>
                {category.icon}
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {category.title}
              </Typography>
            </Box>
          }
        >
          <Grid container spacing={1}>
            {category.reports.map((report, reportIndex) => (
              <Grid item xs={12} key={reportIndex}>
                <Paper
                  onClick={() => console.log('Report clicked:', report)}
                  sx={{
                    padding: 2,
                    cursor: 'pointer',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 2,
                    '&:active': {
                      backgroundColor: 'action.hover',
                      transform: 'scale(0.98)',
                    },
                    transition: 'all 0.2s ease',
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {report}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <MobileButton size="small" variant="outlined" sx={{ minWidth: 'auto', px: 1 }}>
                        View
                      </MobileButton>
                      <MobileButton size="small" variant="text" sx={{ minWidth: 'auto', px: 1 }}>
                        Export
                      </MobileButton>
                    </Box>
                  </Box>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </MobileCard>
      ))}

      {/* Quick Actions */}
      <MobileCard title="Quick Actions">
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              Custom Report
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              Report Builder
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              Export All
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              Schedule Report
            </MobileButton>
          </Grid>
        </Grid>
      </MobileCard>
    </MobileDashboardLayout>
  );
};

export default MobileReports;