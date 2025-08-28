// frontend/src/components/ServiceAnalytics/JobCompletionChart.tsx

import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Box,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Paper
} from '@mui/material';
import {
  CheckCircle as CompletedIcon,
  Schedule as PendingIcon,
  Cancel as CancelledIcon,
  TrendingUp as TrendIcon
} from '@mui/icons-material';
import { JobCompletionMetrics } from '../../services/serviceAnalyticsService';

interface JobCompletionChartProps {
  data: JobCompletionMetrics;
}

const JobCompletionChart: React.FC<JobCompletionChartProps> = ({ data }) => {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'success';
      case 'pending':
      case 'in_progress':
      case 'scheduled':
        return 'warning';
      case 'cancelled':
        return 'error';
      default:
        return 'info';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return <CompletedIcon />;
      case 'pending':
      case 'in_progress':
      case 'scheduled':
        return <PendingIcon />;
      case 'cancelled':
        return <CancelledIcon />;
      default:
        return <TrendIcon />;
    }
  };

  return (
    <Card>
      <CardHeader 
        title="Job Completion Metrics" 
        subheader={`${data.total_jobs} total jobs analyzed`}
      />
      <CardContent>
        {/* Key Metrics Summary */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={6} sm={3}>
            <Box textAlign="center">
              <Typography variant="h5" color="success.main">
                {data.completed_jobs}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Completed
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Box textAlign="center">
              <Typography variant="h5" color="warning.main">
                {data.pending_jobs}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Pending
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Box textAlign="center">
              <Typography variant="h5" color="error.main">
                {data.cancelled_jobs}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Cancelled
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Box textAlign="center">
              <Typography variant="h5" color="primary.main">
                {data.completion_rate.toFixed(1)}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Completion Rate
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Completion Rate Progress Bar */}
        <Box sx={{ mb: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="body2">
              Overall Completion Rate
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {data.completion_rate.toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={data.completion_rate}
            sx={{ height: 8, borderRadius: 4 }}
            color="success"
          />
        </Box>

        {/* On-time Completion Rate */}
        <Box sx={{ mb: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="body2">
              On-time Completion Rate
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {data.on_time_completion_rate.toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={data.on_time_completion_rate}
            sx={{ height: 8, borderRadius: 4 }}
            color="info"
          />
        </Box>

        {/* Average Completion Time */}
        {data.average_completion_time_hours && (
          <Box sx={{ mb: 3 }}>
            <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.default' }}>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography variant="body2">
                  Average Completion Time
                </Typography>
                <Chip
                  label={`${data.average_completion_time_hours.toFixed(1)} hours`}
                  color="primary"
                  variant="outlined"
                  size="small"
                />
              </Box>
            </Paper>
          </Box>
        )}

        {/* Job Status Breakdown */}
        <Box>
          <Typography variant="h6" gutterBottom>
            Job Status Breakdown
          </Typography>
          <Grid container spacing={1}>
            {Object.entries(data.jobs_by_status).map(([status, count]) => (
              <Grid item xs={12} sm={6} key={status}>
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
                      color: `${getStatusColor(status)}.main`,
                      display: 'flex',
                      alignItems: 'center'
                    }}
                  >
                    {getStatusIcon(status)}
                  </Box>
                  <Box flexGrow={1}>
                    <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                      {status.replace('_', ' ')}
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

        {/* Completion Trend Preview */}
        {data.completion_trend.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Completion Trend
            </Typography>
            <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.default' }}>
              <Typography variant="body2" color="text.secondary">
                Last {data.completion_trend.length} days of completion data
              </Typography>
              <Box display="flex" gap={1} mt={1} flexWrap="wrap">
                {data.completion_trend.slice(-7).map((point, index) => (
                  <Chip
                    key={index}
                    label={`${new Date(point.date).toLocaleDateString('en-US', { 
                      month: 'short', 
                      day: 'numeric' 
                    })}: ${point.value}`}
                    size="small"
                    variant="outlined"
                    color={point.value > 0 ? 'success' : 'default'}
                  />
                ))}
              </Box>
            </Paper>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default JobCompletionChart;