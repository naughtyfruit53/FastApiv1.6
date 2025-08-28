// frontend/src/components/ServiceAnalytics/JobVolumeChart.tsx

import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Box,
  Typography,
  Grid,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  TrendingUp as TrendIcon,
  Schedule as VolumeIcon,
  Person as CustomerIcon,
  Flag as PriorityIcon
} from '@mui/icons-material';
import { JobVolumeMetrics } from '../../services/serviceAnalyticsService';

interface JobVolumeChartProps {
  data: JobVolumeMetrics;
}

const JobVolumeChart: React.FC<JobVolumeChartProps> = ({ data }) => {
  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'urgent':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    });
  };

  return (
    <Card>
      <CardHeader 
        title="Job Volume Analytics" 
        subheader={`${data.total_jobs} total jobs analyzed`}
      />
      <CardContent>
        {/* Key Volume Metrics */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={6} sm={3}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
              <Typography variant="h5" color="primary.main">
                {data.total_jobs}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Jobs
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
              <Typography variant="h5" color="info.main">
                {data.jobs_per_day_average.toFixed(1)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Jobs/Day Avg
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
              <Typography variant="h5" color="success.main">
                {data.peak_day_count}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Peak Day Volume
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
              <Typography variant="h5" color="warning.main">
                {data.jobs_by_customer.length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Active Customers
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* Peak Day Information */}
        {data.peak_day && (
          <Box sx={{ mb: 3 }}>
            <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.default' }}>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h6">
                    Peak Day
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Highest job volume recorded
                  </Typography>
                </Box>
                <Box textAlign="right">
                  <Typography variant="h5" color="success.main">
                    {data.peak_day_count}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {formatDate(data.peak_day)}
                  </Typography>
                </Box>
              </Box>
            </Paper>
          </Box>
        )}

        {/* Jobs by Priority */}
        {Object.keys(data.jobs_by_priority).length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Jobs by Priority
            </Typography>
            <Grid container spacing={1}>
              {Object.entries(data.jobs_by_priority).map(([priority, count]) => (
                <Grid item xs={6} sm={3} key={priority}>
                  <Paper 
                    elevation={1} 
                    sx={{ 
                      p: 2, 
                      display: 'flex', 
                      alignItems: 'center',
                      gap: 1,
                      bgcolor: 'background.default'
                    }}
                  >
                    <Box 
                      sx={{ 
                        color: `${getPriorityColor(priority)}.main`,
                        display: 'flex',
                        alignItems: 'center'
                      }}
                    >
                      <PriorityIcon />
                    </Box>
                    <Box flexGrow={1}>
                      <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                        {priority}
                      </Typography>
                      <Typography variant="h6">
                        {count}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {((count / data.total_jobs) * 100).toFixed(1)}%
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Top Customers by Job Volume */}
        {data.jobs_by_customer.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Top Customers by Job Volume
            </Typography>
            <TableContainer component={Paper} elevation={1}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Customer</TableCell>
                    <TableCell align="right">Jobs</TableCell>
                    <TableCell align="right">% of Total</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data.jobs_by_customer.slice(0, 5).map((customer, index) => (
                    <TableRow key={customer.customer_id}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <CustomerIcon fontSize="small" color="action" />
                          <Typography variant="body2">
                            {customer.customer_name}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Chip 
                          label={customer.job_count}
                          size="small"
                          color={index < 3 ? 'primary' : 'default'}
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="text.secondary">
                          {((customer.job_count / data.total_jobs) * 100).toFixed(1)}%
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {/* Volume Trend Preview */}
        {data.volume_trend.length > 0 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Recent Volume Trend
            </Typography>
            <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.default' }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Daily job creation volume
              </Typography>
              <Box display="flex" gap={1} flexWrap="wrap">
                {data.volume_trend.slice(-7).map((point, index) => (
                  <Chip
                    key={index}
                    label={`${formatDate(point.date)}: ${point.value}`}
                    size="small"
                    variant="outlined"
                    color={point.value > data.jobs_per_day_average ? 'success' : 'default'}
                    icon={point.value > data.jobs_per_day_average ? <TrendIcon /> : <VolumeIcon />}
                  />
                ))}
              </Box>
              
              {/* Trend Analysis */}
              <Box mt={2}>
                <Typography variant="body2" color="text.secondary">
                  Trend Analysis:
                </Typography>
                {(() => {
                  const recentTrend = data.volume_trend.slice(-7);
                  const avgRecent = recentTrend.reduce((sum, point) => sum + point.value, 0) / recentTrend.length;
                  const trendDirection = avgRecent > data.jobs_per_day_average ? 'above' : 'below';
                  const trendColor = avgRecent > data.jobs_per_day_average ? 'success.main' : 'warning.main';
                  
                  return (
                    <Typography variant="body2" sx={{ color: trendColor }}>
                      Recent 7-day average ({avgRecent.toFixed(1)} jobs/day) is {trendDirection} overall average
                    </Typography>
                  );
                })()}
              </Box>
            </Paper>
          </Box>
        )}

        {/* No Data State */}
        {data.total_jobs === 0 && (
          <Box textAlign="center" py={4}>
            <Typography variant="body1" color="text.secondary">
              No job volume data available for the selected period.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Job volume metrics will appear here once jobs are created.
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default JobVolumeChart;