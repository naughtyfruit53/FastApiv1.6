/**
 * Streaming Analytics Dashboard Page
 * Real-time streaming data and analytics visualization
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  Container,
  Grid,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Alert,
  LinearProgress,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  CheckCircle as AcknowledgeIcon,
  Check as ResolveIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import streamingAnalyticsService, {
  DataSource,
  StreamingEvent,
  LivePrediction,
  StreamingAlert,
  AlertSeverity,
  AlertStatus,
  DashboardData,
} from '../../services/streamingAnalyticsService';

const StreamingDashboard: React.FC = () => {
  const router = useRouter();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [recentEvents, setRecentEvents] = useState<StreamingEvent[]>([]);
  const [recentPredictions, setRecentPredictions] = useState<LivePrediction[]>([]);
  const [alerts, setAlerts] = useState<StreamingAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    loadDashboardData();
    loadDataSources();
    loadRecentEvents();
    loadRecentPredictions();
    loadAlerts();

    // Set up auto-refresh
    const interval = setInterval(() => {
      loadDashboardData();
      loadRecentEvents();
      loadRecentPredictions();
      loadAlerts();
    }, 30000); // Refresh every 30 seconds

    // Set up WebSocket connection
    const websocket = streamingAnalyticsService.createWebSocketConnection(handleWebSocketMessage);
    if (websocket) {
      setWs(websocket);
      setWsConnected(true);
    }

    return () => {
      clearInterval(interval);
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

  const handleWebSocketMessage = useCallback((data: any) => {
    console.log('WebSocket message received:', data);
    // Handle real-time updates
    if (data.type === 'event') {
      loadRecentEvents();
    } else if (data.type === 'prediction') {
      loadRecentPredictions();
    } else if (data.type === 'alert') {
      loadAlerts();
    }
  }, []);

  const loadDashboardData = async () => {
    try {
      const data = await streamingAnalyticsService.getDashboardData();
      setDashboardData(data);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    }
  };

  const loadDataSources = async () => {
    try {
      const data = await streamingAnalyticsService.listDataSources();
      setDataSources(data);
    } catch (error) {
      console.error('Error loading data sources:', error);
    }
  };

  const loadRecentEvents = async () => {
    try {
      const data = await streamingAnalyticsService.getRecentEvents(undefined, undefined, 60, 50);
      setRecentEvents(data);
    } catch (error) {
      console.error('Error loading recent events:', error);
    }
  };

  const loadRecentPredictions = async () => {
    try {
      const data = await streamingAnalyticsService.getRecentPredictions(undefined, undefined, 60, 50);
      setRecentPredictions(data);
    } catch (error) {
      console.error('Error loading recent predictions:', error);
    }
  };

  const loadAlerts = async () => {
    try {
      const data = await streamingAnalyticsService.getAlerts(AlertStatus.OPEN);
      setAlerts(data);
    } catch (error) {
      console.error('Error loading alerts:', error);
    }
  };

  const handleAcknowledgeAlert = async (alertId: number) => {
    try {
      await streamingAnalyticsService.acknowledgeAlert(alertId);
      loadAlerts();
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  const handleResolveAlert = async (alertId: number) => {
    try {
      await streamingAnalyticsService.resolveAlert(alertId);
      loadAlerts();
    } catch (error) {
      console.error('Error resolving alert:', error);
    }
  };

  const getSeverityIcon = (severity: AlertSeverity) => {
    switch (severity) {
      case AlertSeverity.CRITICAL:
        return <ErrorIcon color="error" />;
      case AlertSeverity.ERROR:
        return <ErrorIcon color="error" />;
      case AlertSeverity.WARNING:
        return <WarningIcon color="warning" />;
      case AlertSeverity.INFO:
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  const getSeverityColor = (severity: AlertSeverity) => {
    switch (severity) {
      case AlertSeverity.CRITICAL:
        return 'error';
      case AlertSeverity.ERROR:
        return 'error';
      case AlertSeverity.WARNING:
        return 'warning';
      case AlertSeverity.INFO:
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1">
            Streaming Analytics Dashboard
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            <Chip
              label={wsConnected ? 'Live' : 'Disconnected'}
              color={wsConnected ? 'success' : 'error'}
              size="small"
              sx={{ mr: 1 }}
            />
            <Typography variant="body2" color="text.secondary">
              Last updated: {dashboardData?.timestamp ? new Date(dashboardData.timestamp).toLocaleTimeString() : '-'}
            </Typography>
          </Box>
        </Box>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={() => {
            loadDashboardData();
            loadRecentEvents();
            loadRecentPredictions();
            loadAlerts();
          }}
        >
          Refresh
        </Button>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Active Data Sources
              </Typography>
              <Typography variant="h3">
                {dashboardData?.active_data_sources || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Events (1h)
              </Typography>
              <Typography variant="h3">
                {dashboardData?.recent_events_1h || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Predictions (1h)
              </Typography>
              <Typography variant="h3">
                {dashboardData?.recent_predictions_1h || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Open Alerts
              </Typography>
              <Typography variant="h3" color="error">
                {dashboardData?.open_alerts || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Alerts Section */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardHeader title="Active Alerts" />
            <CardContent>
              {alerts.length === 0 ? (
                <Alert severity="success">No active alerts</Alert>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Severity</TableCell>
                        <TableCell>Title</TableCell>
                        <TableCell>Time</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {alerts.slice(0, 10).map((alert) => (
                        <TableRow key={alert.id}>
                          <TableCell>
                            <Chip
                              icon={getSeverityIcon(alert.severity)}
                              label={alert.severity}
                              color={getSeverityColor(alert.severity) as any}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">{alert.alert_title}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {alert.alert_message}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            {new Date(alert.triggered_at).toLocaleTimeString()}
                          </TableCell>
                          <TableCell>
                            {alert.status === AlertStatus.OPEN && (
                              <>
                                <IconButton
                                  size="small"
                                  onClick={() => handleAcknowledgeAlert(alert.id)}
                                  title="Acknowledge"
                                >
                                  <AcknowledgeIcon fontSize="small" />
                                </IconButton>
                                <IconButton
                                  size="small"
                                  onClick={() => handleResolveAlert(alert.id)}
                                  title="Resolve"
                                >
                                  <ResolveIcon fontSize="small" />
                                </IconButton>
                              </>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Events Section */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardHeader title="Recent Events" subheader="Last 50 events" />
            <CardContent>
              <TableContainer sx={{ maxHeight: 400 }}>
                <Table size="small" stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell>Event Type</TableCell>
                      <TableCell>Timestamp</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentEvents.map((event) => (
                      <TableRow key={event.id}>
                        <TableCell>{event.event_type}</TableCell>
                        <TableCell>
                          {new Date(event.event_timestamp).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={event.processed ? 'Processed' : 'Pending'}
                            color={event.processed ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Predictions Section */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Recent Predictions" subheader="Last 50 predictions" />
            <CardContent>
              <TableContainer sx={{ maxHeight: 400 }}>
                <Table size="small" stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell>Prediction Type</TableCell>
                      <TableCell>Confidence</TableCell>
                      <TableCell>Result</TableCell>
                      <TableCell>Timestamp</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentPredictions.map((prediction) => (
                      <TableRow key={prediction.id}>
                        <TableCell>{prediction.prediction_type}</TableCell>
                        <TableCell>
                          {prediction.confidence_score
                            ? `${(prediction.confidence_score * 100).toFixed(1)}%`
                            : '-'}
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                            {JSON.stringify(prediction.prediction_result).substring(0, 50)}...
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {new Date(prediction.predicted_at).toLocaleString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Data Sources Section */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Data Sources" />
            <CardContent>
              <Grid container spacing={2}>
                {dataSources.map((source) => (
                  <Grid item xs={12} sm={6} md={4} key={source.id}>
                    <Paper sx={{ p: 2 }}>
                      <Typography variant="h6" gutterBottom>
                        {source.source_name}
                      </Typography>
                      <Chip
                        label={source.status}
                        color={source.is_active ? 'success' : 'default'}
                        size="small"
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="body2" color="text.secondary">
                        Type: {source.source_type}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Messages: {source.message_count}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Errors: {source.error_count}
                      </Typography>
                      {source.last_message_at && (
                        <Typography variant="caption" color="text.secondary">
                          Last message: {new Date(source.last_message_at).toLocaleString()}
                        </Typography>
                      )}
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default StreamingDashboard;
