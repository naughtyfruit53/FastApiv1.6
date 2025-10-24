// components/PredictiveDashboard.tsx
// Predictive analytics dashboard with ML models and predictions
import React, { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
} from "@mui/material";
import {
  TrendingUp,
  CheckCircle,
  Error as ErrorIcon,
  AccessTime,
} from "@mui/icons-material";
import { mlAnalyticsService, MLAnalyticsDashboard } from "../services/analyticsService";

const PredictiveDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dashboardData, setDashboardData] = useState<MLAnalyticsDashboard | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await mlAnalyticsService.getDashboard();
      setDashboardData(data);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!dashboardData) {
    return (
      <Alert severity="info" sx={{ mb: 2 }}>
        No dashboard data available
      </Alert>
    );
  }

  const getModelStatusColor = (isActive: boolean): "success" | "default" => {
    return isActive ? "success" : "default";
  };

  const getSeverityColor = (severity: string): "error" | "warning" | "info" | "default" => {
    switch (severity) {
      case "critical":
        return "error";
      case "high":
        return "error";
      case "medium":
        return "warning";
      case "low":
        return "info";
      default:
        return "default";
    }
  };

  return (
    <Box>
      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Total Models
              </Typography>
              <Typography variant="h3">{dashboardData.total_models}</Typography>
              <Typography variant="body2" color="text.secondary">
                {dashboardData.active_models} active
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Total Predictions
              </Typography>
              <Typography variant="h3">{dashboardData.total_predictions}</Typography>
              <Typography variant="body2" color="text.secondary">
                Across all models
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Unresolved Anomalies
              </Typography>
              <Typography variant="h3" color={dashboardData.unresolved_anomalies > 0 ? "error" : "success"}>
                {dashboardData.unresolved_anomalies}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {dashboardData.total_anomalies_detected} total detected
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Model Performance Summary */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <TrendingUp />
            Model Performance Summary
          </Typography>
          {dashboardData.model_performance_summary.length > 0 ? (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Model Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell align="right">Accuracy</TableCell>
                    <TableCell align="right">Predictions</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {dashboardData.model_performance_summary.map((model: any) => (
                    <TableRow key={model.model_id}>
                      <TableCell>{model.model_name}</TableCell>
                      <TableCell>
                        <Chip label={model.model_type} size="small" />
                      </TableCell>
                      <TableCell align="right">
                        {model.accuracy_score ? (
                          <Box>
                            <Typography variant="body2">
                              {(model.accuracy_score * 100).toFixed(1)}%
                            </Typography>
                            <LinearProgress
                              variant="determinate"
                              value={model.accuracy_score * 100}
                              sx={{ mt: 0.5, height: 6, borderRadius: 1 }}
                            />
                          </Box>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            N/A
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell align="right">{model.prediction_count}</TableCell>
                      <TableCell>
                        <Chip
                          icon={model.is_active ? <CheckCircle /> : <AccessTime />}
                          label={model.is_active ? "Active" : "Inactive"}
                          color={getModelStatusColor(model.is_active)}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Alert severity="info">No models available</Alert>
          )}
        </CardContent>
      </Card>

      {/* Recent Anomalies */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <ErrorIcon />
            Recent Anomalies
          </Typography>
          {dashboardData.recent_anomalies.length > 0 ? (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Detected At</TableCell>
                    <TableCell>Severity</TableCell>
                    <TableCell align="right">Anomaly Score</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {dashboardData.recent_anomalies.map((anomaly: any) => (
                    <TableRow key={anomaly.id}>
                      <TableCell>
                        {new Date(anomaly.detected_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={anomaly.severity}
                          color={getSeverityColor(anomaly.severity)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        {anomaly.anomaly_score.toFixed(2)}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={anomaly.is_resolved ? "Resolved" : "Open"}
                          color={anomaly.is_resolved ? "success" : "warning"}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Alert severity="success">No anomalies detected recently</Alert>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default PredictiveDashboard;
