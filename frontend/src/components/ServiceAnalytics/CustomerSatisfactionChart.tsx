// frontend/src/components/ServiceAnalytics/CustomerSatisfactionChart.tsx

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
  Rating
} from '@mui/material';
import {
  SentimentVerySatisfied as VeryHappyIcon,
  SentimentSatisfied as HappyIcon,
  SentimentNeutral as NeutralIcon,
  SentimentDissatisfied as UnhappyIcon,
  ThumbUp as RecommendIcon,
  TrendingUp as TrendIcon
} from '@mui/icons-material';
import { CustomerSatisfactionMetrics } from '../../services/serviceAnalyticsService';

interface CustomerSatisfactionChartProps {
  data: CustomerSatisfactionMetrics;
}

const CustomerSatisfactionChart: React.FC<CustomerSatisfactionChartProps> = ({ data }) => {
  const getSatisfactionColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'satisfied':
        return 'success';
      case 'neutral':
        return 'warning';
      case 'dissatisfied':
        return 'error';
      default:
        return 'info';
    }
  };

  const getSatisfactionIcon = (level: string) => {
    switch (level.toLowerCase()) {
      case 'satisfied':
        return <VeryHappyIcon />;
      case 'neutral':
        return <NeutralIcon />;
      case 'dissatisfied':
        return <UnhappyIcon />;
      default:
        return <HappyIcon />;
    }
  };

  const getRatingColor = (rating: number) => {
    if (rating >= 4) return 'success.main';
    if (rating >= 3) return 'warning.main';
    return 'error.main';
  };

  const formatRating = (rating?: number) => {
    return rating ? rating.toFixed(1) : 'N/A';
  };

  return (
    <Card>
      <CardHeader 
        title="Customer Satisfaction" 
        subheader={`${data.total_feedback_received} feedback responses analyzed`}
      />
      <CardContent>
        {/* Overall Rating */}
        <Box sx={{ mb: 3, textAlign: 'center' }}>
          <Typography variant="h3" sx={{ color: getRatingColor(data.average_overall_rating) }}>
            {formatRating(data.average_overall_rating)}
          </Typography>
          <Rating 
            value={data.average_overall_rating} 
            readOnly 
            precision={0.1}
            size="large"
          />
          <Typography variant="body2" color="text.secondary">
            Overall Rating (out of 5)
          </Typography>
        </Box>

        {/* Rating Breakdown */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={6} sm={3}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
              <Typography variant="h6" sx={{ color: getRatingColor(data.average_service_quality || 0) }}>
                {formatRating(data.average_service_quality)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Service Quality
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
              <Typography variant="h6" sx={{ color: getRatingColor(data.average_technician_rating || 0) }}>
                {formatRating(data.average_technician_rating)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Technician
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
              <Typography variant="h6" sx={{ color: getRatingColor(data.average_timeliness_rating || 0) }}>
                {formatRating(data.average_timeliness_rating)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Timeliness
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={6} sm={3}>
            <Paper elevation={1} sx={{ p: 2, textAlign: 'center', bgcolor: 'background.default' }}>
              <Typography variant="h6" sx={{ color: getRatingColor(data.average_communication_rating || 0) }}>
                {formatRating(data.average_communication_rating)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Communication
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* NPS Score */}
        {data.nps_score !== null && data.nps_score !== undefined && (
          <Box sx={{ mb: 3 }}>
            <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.default' }}>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h6">
                    Net Promoter Score (NPS)
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Customer recommendation likelihood
                  </Typography>
                </Box>
                <Chip
                  label={`${data.nps_score.toFixed(1)}`}
                  color={data.nps_score > 0 ? 'success' : data.nps_score < 0 ? 'error' : 'warning'}
                  size="large"
                />
              </Box>
            </Paper>
          </Box>
        )}

        {/* Recommendation Rate */}
        {data.recommendation_rate !== null && data.recommendation_rate !== undefined && (
          <Box sx={{ mb: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Box display="flex" alignItems="center" gap={1}>
                <RecommendIcon color="primary" />
                <Typography variant="body2">
                  Would Recommend
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                {data.recommendation_rate.toFixed(1)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={data.recommendation_rate}
              sx={{ height: 8, borderRadius: 4 }}
              color="success"
            />
          </Box>
        )}

        {/* Satisfaction Distribution */}
        {Object.keys(data.satisfaction_distribution).length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Satisfaction Distribution
            </Typography>
            <Grid container spacing={1}>
              {Object.entries(data.satisfaction_distribution).map(([level, count]) => (
                <Grid item xs={12} sm={4} key={level}>
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
                        color: `${getSatisfactionColor(level)}.main`,
                        display: 'flex',
                        alignItems: 'center'
                      }}
                    >
                      {getSatisfactionIcon(level)}
                    </Box>
                    <Box flexGrow={1}>
                      <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                        {level}
                      </Typography>
                      <Typography variant="h6">
                        {count}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {data.total_feedback_received > 0 
                        ? ((count / data.total_feedback_received) * 100).toFixed(1)
                        : 0}%
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Satisfaction Trend Preview */}
        {data.satisfaction_trend.length > 0 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Recent Satisfaction Trend
            </Typography>
            <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.default' }}>
              <Typography variant="body2" color="text.secondary">
                Average daily satisfaction ratings
              </Typography>
              <Box display="flex" gap={1} mt={1} flexWrap="wrap">
                {data.satisfaction_trend.slice(-7).map((point, index) => (
                  <Chip
                    key={index}
                    label={`${new Date(point.date).toLocaleDateString('en-US', { 
                      month: 'short', 
                      day: 'numeric' 
                    })}: ${point.value}/5`}
                    size="small"
                    variant="outlined"
                    color={point.value >= 4 ? 'success' : point.value >= 3 ? 'warning' : 'error'}
                  />
                ))}
              </Box>
            </Paper>
          </Box>
        )}

        {/* No Data State */}
        {data.total_feedback_received === 0 && (
          <Box textAlign="center" py={4}>
            <Typography variant="body1" color="text.secondary">
              No customer feedback data available for the selected period.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Encourage customers to provide feedback after job completion.
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default CustomerSatisfactionChart;