/**
 * Live Analytics Dashboard Component
 * Reusable component for displaying live streaming analytics
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Grid,
  Paper,
  Typography,
  LinearProgress,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as RemoveIcon,
} from '@mui/icons-material';
import streamingAnalyticsService, {
  DashboardData,
  StreamingMetric,
} from '../services/streamingAnalyticsService';

interface LiveAnalyticsDashboardProps {
  refreshInterval?: number;
  onDataUpdate?: (data: DashboardData) => void;
}

interface MetricTrend {
  current: number;
  previous: number;
  change: number;
  changePercent: number;
  trend: 'up' | 'down' | 'stable';
}

const LiveAnalyticsDashboard: React.FC<LiveAnalyticsDashboardProps> = ({
  refreshInterval = 10000,
  onDataUpdate,
}) => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [metrics, setMetrics] = useState<StreamingMetric[]>([]);
  const [metricTrends, setMetricTrends] = useState<Record<string, MetricTrend>>({});
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    loadDashboardData();
    loadMetrics();

    // Set up auto-refresh
    const interval = setInterval(() => {
      loadDashboardData();
      loadMetrics();
    }, refreshInterval);

    // Set up WebSocket connection
    const ws = streamingAnalyticsService.createWebSocketConnection(handleWebSocketMessage);
    if (ws) {
      setWsConnected(true);
    }

    return () => {
      clearInterval(interval);
      if (ws) {
        ws.close();
      }
    };
  }, [refreshInterval]);

  const handleWebSocketMessage = useCallback((data: any) => {
    console.log('Live analytics WebSocket message:', data);
    // Refresh data on receiving messages
    loadDashboardData();
    loadMetrics();
  }, []);

  const loadDashboardData = async () => {
    try {
      const data = await streamingAnalyticsService.getDashboardData();
      setDashboardData(data);
      if (onDataUpdate) {
        onDataUpdate(data);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    try {
      const data = await streamingAnalyticsService.getMetrics(undefined, '1m', 100);
      setMetrics(data);
      calculateTrends(data);
    } catch (error) {
      console.error('Error loading metrics:', error);
    }
  };

  const calculateTrends = (metricsData: StreamingMetric[]) => {
    const trends: Record<string, MetricTrend> = {};

    // Group metrics by name
    const metricsByName: Record<string, StreamingMetric[]> = {};
    metricsData.forEach((metric) => {
      if (!metricsByName[metric.metric_name]) {
        metricsByName[metric.metric_name] = [];
      }
      metricsByName[metric.metric_name].push(metric);
    });

    // Calculate trends for each metric
    Object.entries(metricsByName).forEach(([name, metricList]) => {
      if (metricList.length >= 2) {
        // Sort by window_start descending
        const sorted = [...metricList].sort(
          (a, b) => new Date(b.window_start).getTime() - new Date(a.window_start).getTime()
        );

        const current = sorted[0].metric_value;
        const previous = sorted[1].metric_value;
        const change = current - previous;
        const changePercent = previous !== 0 ? (change / previous) * 100 : 0;

        let trend: 'up' | 'down' | 'stable' = 'stable';
        if (Math.abs(changePercent) > 5) {
          trend = change > 0 ? 'up' : 'down';
        }

        trends[name] = {
          current,
          previous,
          change,
          changePercent,
          trend,
        };
      }
    });

    setMetricTrends(trends);
  };

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return <TrendingUpIcon color="success" />;
      case 'down':
        return <TrendingDownIcon color="error" />;
      case 'stable':
        return <RemoveIcon color="action" />;
    }
  };

  const getTrendColor = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return 'success';
      case 'down':
        return 'error';
      case 'stable':
        return 'default';
    }
  };

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      {/* Connection Status */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Live Analytics</Typography>
        <Chip
          label={wsConnected ? 'Live' : 'Disconnected'}
          color={wsConnected ? 'success' : 'error'}
          size="small"
        />
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" variant="body2" gutterBottom>
                Active Sources
              </Typography>
              <Typography variant="h4">
                {dashboardData?.active_data_sources || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" variant="body2" gutterBottom>
                Events (1h)
              </Typography>
              <Typography variant="h4">
                {dashboardData?.recent_events_1h || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" variant="body2" gutterBottom>
                Predictions (1h)
              </Typography>
              <Typography variant="h4">
                {dashboardData?.recent_predictions_1h || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" variant="body2" gutterBottom>
                Open Alerts
              </Typography>
              <Typography variant="h4" color="error.main">
                {dashboardData?.open_alerts || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Metric Trends */}
      {Object.keys(metricTrends).length > 0 && (
        <Card>
          <CardHeader title="Metric Trends" subheader="Real-time metric changes" />
          <CardContent>
            <Grid container spacing={2}>
              {Object.entries(metricTrends).map(([metricName, trend]) => (
                <Grid item xs={12} sm={6} md={4} key={metricName}>
                  <Paper sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {metricName}
                        </Typography>
                        <Typography variant="h5">
                          {trend.current.toFixed(2)}
                        </Typography>
                      </Box>
                      {getTrendIcon(trend.trend)}
                    </Box>
                    <Box sx={{ mt: 1 }}>
                      <Chip
                        label={`${trend.changePercent >= 0 ? '+' : ''}${trend.changePercent.toFixed(1)}%`}
                        color={getTrendColor(trend.trend) as any}
                        size="small"
                      />
                      <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                        vs previous
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Last Update */}
      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          Last updated: {dashboardData?.timestamp ? new Date(dashboardData.timestamp).toLocaleString() : '-'}
        </Typography>
      </Box>
    </Box>
  );
};

export default LiveAnalyticsDashboard;
