/**
 * AI Analytics Dashboard
 * Overview of AI models, predictions, anomalies, and insights
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  Psychology as AIIcon,
  TrendingUp as TrendingIcon,
  Warning as WarningIcon,
  Lightbulb as InsightIcon,
  AutoAwesome as AutoIcon
} from '@mui/icons-material';
import aiService, { AIAnalyticsDashboard, AIModel } from '../services/aiService';

import { ProtectedPage } from '../components/ProtectedPage';
const AIAnalyticsPage: React.FC = () => {
  const [dashboard, setDashboard] = useState<AIAnalyticsDashboard | null>(null);
  const [models, setModels] = useState<AIModel[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [dashboardData, modelsData] = await Promise.all([
        aiService.getAIAnalyticsDashboard(),
        aiService.getAIModels()
      ]);
      
      setDashboard(dashboardData);
      setModels(modelsData);
    } catch (error) {
      console.error('Error loading AI analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <ProtectedPage moduleKey="ai" action="read">
      rotectedPage moduleKey="ai" action="read">
        ox sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
        <CircularProgress />
      </Box>
      </ProtectedPage>
    );
  }
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <AIIcon fontSize="large" color="primary" />
        AI Analytics Dashboard
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total AI Models
              </Typography>
              <Typography variant="h4">{dashboard?.total_models || 0}</Typography>
              <Typography variant="caption" color="success.main">
                {dashboard?.active_models || 0} active
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Predictions Today
              </Typography>
              <Typography variant="h4">{dashboard?.total_predictions_today || 0}</Typography>
              <Typography variant="caption" color="text.secondary">
                {dashboard?.total_predictions_month || 0} this month
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Active Anomalies
              </Typography>
              <Typography variant="h4">{dashboard?.active_anomalies || 0}</Typography>
              <Typography variant="caption" color="error.main">
                {dashboard?.critical_anomalies || 0} critical
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                AI Insights
              </Typography>
              <Typography variant="h4">{dashboard?.active_insights || 0}</Typography>
              <Typography variant="caption" color="warning.main">
                {dashboard?.high_priority_insights || 0} high priority
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* AI Models Table */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TrendingIcon />
          AI Models
        </Typography>
        
        {models.length === 0 ? (
          <Typography color="text.secondary">No AI models configured yet.</Typography>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Model Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Accuracy</TableCell>
                  <TableCell>Predictions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {models.map((model) => (
                  <TableRow key={model.id}>
                    <TableCell>{model.model_name}</TableCell>
                    <TableCell>
                      <Chip label={model.model_type} size="small" />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={model.status}
                        size="small"
                        color={model.status === 'deployed' ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      {model.accuracy_score ? `${(model.accuracy_score * 100).toFixed(1)}%` : 'N/A'}
                    </TableCell>
                    <TableCell>{model.prediction_count}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* Quick Actions */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button variant="outlined" startIcon={<AIIcon />}>
            Create New Model
          </Button>
          <Button variant="outlined" startIcon={<TrendingIcon />}>
            Run Predictions
          </Button>
          <Button variant="outlined" startIcon={<WarningIcon />}>
            Detect Anomalies
          </Button>
          <Button variant="outlined" startIcon={<InsightIcon />}>
            Generate Insights
          </Button>
          <Button variant="outlined" startIcon={<AutoIcon />}>
            Automation Workflows
          </Button>
        </Box>
      </Paper>
    </Container>
    </ProtectedPage>
  );
};
export default AIAnalyticsPage;
