// frontend/src/components/ServiceAnalytics/SLAComplianceChart.tsx

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
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  CheckCircle as ComplianceIcon,
  Warning as BreachIcon,
  Speed as PerformanceIcon,
  Error as ErrorIcon,
  Schedule as TimeIcon
} from '@mui/icons-material';
import { SLAComplianceMetrics } from '../../services/serviceAnalyticsService';

interface SLAComplianceChartProps {
  data: SLAComplianceMetrics;
}

const SLAComplianceChart: React.FC<SLAComplianceChartProps> = ({ data }) => {
  const getComplianceColor = (rate: number) => {
    if (rate >= 95) return 'success';
    if (rate >= 85) return 'info';
    if (rate >= 70) return 'warning';
    return 'error';
  };

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

  const formatTime = (hours?: number) => {
    if (!hours) return 'N/A';
    if (hours < 1) return `${(hours * 60).toFixed(0)}m`;
    if (hours < 24) return `${hours.toFixed(1)}h`;
    return `${(hours / 24).toFixed(1)}d`;
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
        title="SLA Compliance" 
        subheader={`${data.total_jobs_with_sla} jobs with SLA requirements analyzed`}
      />
      <CardContent>
        {data.total_jobs_with_sla === 0 ? (
          <Box textAlign="center" py={4}>
            <Typography variant="body1" color="text.secondary">
              No SLA compliance data available for the selected period.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              SLA metrics will appear here once SLA policies are configured and jobs are tracked.
            </Typography>
          </Box>
        ) : (
          <>
            {/* Overall Compliance Rate */}
            <Box sx={{ mb: 3, textAlign: 'center' }}>
              <Typography variant="h3" sx={{ color: `${getComplianceColor(data.overall_compliance_rate)}.main` }}>
                {data.overall_compliance_rate.toFixed(1)}%
              </Typography>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Overall SLA Compliance Rate
              </Typography>
              <LinearProgress
                variant="determinate"
                value={data.overall_compliance_rate}
                sx={{ height: 12, borderRadius: 6, maxWidth: 300, mx: 'auto' }}
                color={getComplianceColor(data.overall_compliance_rate)}
              />
            </Box>

            {/* Key Metrics Summary */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={6} sm={3}>
                <Paper elevation={1} sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
                  <Typography variant="h5" color="success.main">
                    {data.sla_met_count}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    SLA Met
                  </Typography>
                </Paper>
              </Grid>
              
              <Grid item xs={6} sm={3}>
                <Paper elevation={1} sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
                  <Typography variant="h5" color="error.main">
                    {data.sla_breached_count}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    SLA Breached
                  </Typography>
                </Paper>
              </Grid>
              
              <Grid item xs={6} sm={3}>
                <Paper elevation={1} sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
                  <Typography variant="h5" color="primary.main">
                    {data.total_jobs_with_sla}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Total with SLA
                  </Typography>
                </Paper>
              </Grid>
              
              <Grid item xs={6} sm={3}>
                <Paper elevation={1} sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
                  <Typography variant="h5" color="info.main">
                    {formatTime(data.average_resolution_time_hours)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Avg Resolution
                  </Typography>
                </Paper>
              </Grid>
            </Grid>

            {/* Compliance by Priority */}
            {Object.keys(data.compliance_by_priority).length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Compliance by Priority
                </Typography>
                <Grid container spacing={1}>
                  {Object.entries(data.compliance_by_priority).map(([priority, rate]) => (
                    <Grid item xs={12} sm={6} md={3} key={priority}>
                      <Paper 
                        elevation={1} 
                        sx={{ 
                          p: 2, 
                          bgcolor: 'background.default'
                        }}
                      >
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                          <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                            {priority}
                          </Typography>
                          <Chip
                            size="small"
                            label={`${rate.toFixed(1)}%`}
                            color={getComplianceColor(rate)}
                          />
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={rate}
                          sx={{ height: 6, borderRadius: 3 }}
                          color={getComplianceColor(rate)}
                        />
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}

            {/* SLA Breach Reasons */}
            {Object.keys(data.breach_reasons).length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Common Breach Reasons
                </Typography>
                <TableContainer component={Paper} elevation={1}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Reason</TableCell>
                        <TableCell align="center">Occurrences</TableCell>
                        <TableCell align="center">% of Breaches</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(data.breach_reasons)
                        .sort(([, a], [, b]) => b - a)
                        .map(([reason, count]) => (
                          <TableRow key={reason}>
                            <TableCell>
                              <Box display="flex" alignItems="center" gap={1}>
                                <ErrorIcon fontSize="small" color="error" />
                                <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                                  {reason.replace('_', ' ')}
                                </Typography>
                              </Box>
                            </TableCell>
                            <TableCell align="center">
                              <Chip 
                                label={count}
                                size="small"
                                color="error"
                                variant="outlined"
                              />
                            </TableCell>
                            <TableCell align="center">
                              <Typography variant="body2" color="text.secondary">
                                {data.sla_breached_count > 0 
                                  ? ((count / data.sla_breached_count) * 100).toFixed(1)
                                  : 0}%
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}

            {/* Compliance Trend Preview */}
            {data.compliance_trend.length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Recent Compliance Trend
                </Typography>
                <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.default' }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Daily SLA compliance rates
                  </Typography>
                  <Box display="flex" gap={1} flexWrap="wrap">
                    {data.compliance_trend.slice(-7).map((point, index) => (
                      <Chip
                        key={index}
                        label={`${formatDate(point.date)}: ${point.value.toFixed(1)}%`}
                        size="small"
                        variant="outlined"
                        color={getComplianceColor(point.value)}
                        icon={point.value >= 85 ? <ComplianceIcon /> : <BreachIcon />}
                      />
                    ))}
                  </Box>
                  
                  {/* Trend Analysis */}
                  <Box mt={2}>
                    <Typography variant="body2" color="text.secondary">
                      Trend Analysis:
                    </Typography>
                    {(() => {
                      const recentTrend = data.compliance_trend.slice(-7);
                      const avgRecent = recentTrend.reduce((sum, point) => sum + point.value, 0) / recentTrend.length;
                      const trendDirection = avgRecent > data.overall_compliance_rate ? 'improving' : 'declining';
                      const trendColor = avgRecent > data.overall_compliance_rate ? 'success.main' : 'warning.main';
                      
                      return (
                        <Typography variant="body2" sx={{ color: trendColor }}>
                          Recent 7-day average ({avgRecent.toFixed(1)}%) shows {trendDirection} trend
                        </Typography>
                      );
                    })()}
                  </Box>
                </Paper>
              </Box>
            )}

            {/* Performance Indicators */}
            <Box>
              <Typography variant="h6" gutterBottom>
                Performance Indicators
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.default' }}>
                    <Box display="flex" alignItems="center" gap={2}>
                      <PerformanceIcon color={getComplianceColor(data.overall_compliance_rate)} />
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Compliance Status
                        </Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {data.overall_compliance_rate >= 95 ? 'Excellent' :
                           data.overall_compliance_rate >= 85 ? 'Good' :
                           data.overall_compliance_rate >= 70 ? 'Needs Improvement' : 'Critical'}
                        </Typography>
                      </Box>
                    </Box>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.default' }}>
                    <Box display="flex" alignItems="center" gap={2}>
                      <TimeIcon color="action" />
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Resolution Performance
                        </Typography>
                        <Typography variant="body1" fontWeight="medium">
                          {data.average_resolution_time_hours 
                            ? `${formatTime(data.average_resolution_time_hours)} average`
                            : 'No data available'}
                        </Typography>
                      </Box>
                    </Box>
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default SLAComplianceChart;