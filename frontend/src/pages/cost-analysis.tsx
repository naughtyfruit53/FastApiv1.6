// frontend/src/pages/cost-analysis.tsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Paper,
  Chip,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Warning,
  Lightbulb,
  CheckCircle,
  Error,
  Info,
  Timeline
} from '@mui/icons-material';
import DashboardLayout from '../components/DashboardLayout';
import api from '../lib/api';
import { formatCurrency } from "../utils/currencyUtils";

import { ProtectedPage } from '../components/ProtectedPage';
interface CostCenter {
  id: number;
  cost_center_name: string;
  budget_amount: number;
  actual_amount: number;
  department: string;
}

interface Insight {
  type: 'warning' | 'success' | 'info' | 'recommendation';
  icon: React.ReactNode;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
}

const CostAnalysisPage: React.FC = () => {
  const [costCenters, setCostCenters] = useState<CostCenter[]>([]);
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [metrics, setMetrics] = useState({
    totalSpend: 0,
    budgetVariance: 0,
    averageUtilization: 0,
    topSpenders: [] as CostCenter[],
    underutilized: [] as CostCenter[]
  });

  useEffect(() => {
    fetchCostAnalysis();
  }, []);

  const fetchCostAnalysis = async () => {
    try {
      setLoading(true);
      const response = await api.get('/erp/cost-centers');
      const centers: CostCenter[] = response.data || [];
      setCostCenters(centers);

      // Calculate metrics
      const totalSpend = centers.reduce((sum, cc) => sum + (cc.actual_amount || 0), 0);
      const totalBudget = centers.reduce((sum, cc) => sum + (cc.budget_amount || 0), 0);
      const budgetVariance = totalBudget > 0 ? ((totalSpend - totalBudget) / totalBudget) * 100 : 0;
      const averageUtilization = totalBudget > 0 ? (totalSpend / totalBudget) * 100 : 0;

      // Top spenders
      const topSpenders = [...centers]
        .sort((a, b) => (b.actual_amount || 0) - (a.actual_amount || 0))
        .slice(0, 5);

      // Underutilized (spending less than 50% of budget)
      const underutilized = centers.filter(cc => {
        const utilization = cc.budget_amount > 0 ? (cc.actual_amount / cc.budget_amount) * 100 : 0;
        return utilization < 50 && cc.budget_amount > 0;
      });

      setMetrics({
        totalSpend,
        budgetVariance,
        averageUtilization,
        topSpenders,
        underutilized
      });

      // Generate smart insights
      generateInsights(centers, budgetVariance, averageUtilization);
    } catch (error) {
      console.error('Error fetching cost analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateInsights = (centers: CostCenter[], variance: number, utilization: number) => {
    const newInsights: Insight[] = [];

    // Budget variance insights
    if (variance > 10) {
      newInsights.push({
        type: 'warning',
        icon: <Warning color="warning" />,
        title: 'Budget Overrun Detected',
        description: `Organization is ${variance.toFixed(1)}% over budget. Immediate cost control measures recommended.`,
        priority: 'high'
      });
    } else if (variance > 5) {
      newInsights.push({
        type: 'info',
        icon: <Info color="info" />,
        title: 'Approaching Budget Limit',
        description: `Spending is ${variance.toFixed(1)}% over budget. Monitor spending closely.`,
        priority: 'medium'
      });
    } else if (variance < -20) {
      newInsights.push({
        type: 'success',
        icon: <CheckCircle color="success" />,
        title: 'Excellent Budget Management',
        description: `Organization is ${Math.abs(variance).toFixed(1)}% under budget. Well controlled spending.`,
        priority: 'low'
      });
    }

    // Utilization insights
    if (utilization > 90) {
      newInsights.push({
        type: 'warning',
        icon: <Warning color="warning" />,
        title: 'High Budget Utilization',
        description: `${utilization.toFixed(1)}% of budget utilized. Consider budget increase or expense reduction.`,
        priority: 'high'
      });
    } else if (utilization < 60) {
      newInsights.push({
        type: 'recommendation',
        icon: <Lightbulb color="primary" />,
        title: 'Underutilized Budget',
        description: `Only ${utilization.toFixed(1)}% of budget utilized. Review budget allocation or increase activities.`,
        priority: 'medium'
      });
    }

    // Cost center specific insights
    const overBudgetCenters = centers.filter(cc => 
      cc.actual_amount > cc.budget_amount && cc.budget_amount > 0
    );

    if (overBudgetCenters.length > 0) {
      newInsights.push({
        type: 'warning',
        icon: <Error color="error" />,
        title: 'Cost Centers Over Budget',
        description: `${overBudgetCenters.length} cost center(s) have exceeded their budgets. Review: ${overBudgetCenters.slice(0, 2).map(cc => cc.cost_center_name).join(', ')}`,
        priority: 'high'
      });
    }

    // Identify inefficiencies
    const highSpendLowBudget = centers.filter(cc => {
      const utilization = cc.budget_amount > 0 ? (cc.actual_amount / cc.budget_amount) * 100 : 0;
      return utilization > 120;
    });

    if (highSpendLowBudget.length > 0) {
      newInsights.push({
        type: 'recommendation',
        icon: <Lightbulb color="primary" />,
        title: 'Budget Reallocation Opportunity',
        description: `${highSpendLowBudget.length} cost center(s) consistently overspend. Consider budget reallocation.`,
        priority: 'medium'
      });
    }

    // Trend analysis
    newInsights.push({
      type: 'info',
      icon: <Timeline color="info" />,
      title: 'Cost Trend Analysis',
      description: `Top spending areas: ${centers.slice(0, 3).map(cc => cc.cost_center_name).join(', ')}. Monitor these areas for cost optimization opportunities.`,
      priority: 'low'
    });

    setInsights(newInsights);
  };

  const getInsightColor = (type: string) => {
    switch (type) {
      case 'warning':
        return 'warning';
      case 'success':
        return 'success';
      case 'recommendation':
        return 'primary';
      default:
        return 'info';
    }
  };

  const getPriorityChip = (priority: string) => {
    const colors: any = {
      high: 'error',
      medium: 'warning',
      low: 'success'
    };
    return (
      <ProtectedPage moduleKey="finance" action="read">
      hip
        label={priority.toUpperCase()}
        color={colors[priority]}
        size="small"
      />
    );
  };

  if (loading) {
    return (
      <ProtectedPage moduleKey="finance" action="read">
        ashboardLayout
        title="Cost Analysis"
        subtitle="Analyze spending patterns and get actionable insights"
      >
        <LinearProgress />
      </DashboardLayout>
      </ProtectedPage>
    );
  }
  return (
    <DashboardLayout
      title="Cost Analysis"
      subtitle="AI-powered insights to optimize spending and improve budget efficiency"
    >
      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingUp color="primary" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Total Spend
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">
                {formatCurrency(metrics.totalSpend)}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Across all cost centers
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingDown color={metrics.budgetVariance > 0 ? 'error' : 'success'} sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Budget Variance
                </Typography>
              </Box>
              <Typography 
                variant="h5" 
                fontWeight="bold"
                color={metrics.budgetVariance > 0 ? 'error' : 'success'}
              >
                {metrics.budgetVariance > 0 ? '+' : ''}{metrics.budgetVariance.toFixed(1)}%
              </Typography>
              <Typography variant="caption" color="textSecondary">
                {metrics.budgetVariance > 0 ? 'Over' : 'Under'} budget
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <CheckCircle color="info" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Avg Utilization
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold" color="info.main">
                {metrics.averageUtilization.toFixed(1)}%
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Budget utilized
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Warning color="warning" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Active Insights
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold" color="warning.main">
                {insights.filter(i => i.priority === 'high').length}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                High priority items
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Smart Insights */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Smart Insights & Recommendations
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                AI-powered analysis of your spending patterns and budget performance
              </Typography>

              {insights.length === 0 ? (
                <Alert severity="success">
                  <Typography variant="body2">
                    No critical issues detected. Your budget management is on track!
                  </Typography>
                </Alert>
              ) : (
                <List>
                  {insights.map((insight, index) => (
                    <React.Fragment key={index}>
                      <ListItem alignItems="flex-start">
                        <ListItemIcon>
                          {insight.icon}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box display="flex" alignItems="center" gap={1}>
                              <Typography variant="subtitle2">{insight.title}</Typography>
                              {getPriorityChip(insight.priority)}
                            </Box>
                          }
                          secondary={
                            <Typography variant="body2" color="text.secondary">
                              {insight.description}
                            </Typography>
                          }
                        />
                      </ListItem>
                      {index < insights.length - 1 && <Divider variant="inset" component="li" />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Top Spenders */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Cost Centers
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                Highest spending areas
              </Typography>

              <List>
                {metrics.topSpenders.map((cc, index) => (
                  <ListItem key={cc.id}>
                    <ListItemText
                      primary={
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="body2" fontWeight="600">
                            {index + 1}. {cc.cost_center_name}
                          </Typography>
                          <Typography variant="body2" fontWeight="bold" color="primary">
                            {formatCurrency(cc.actual_amount)}
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <Box mt={0.5}>
                          <LinearProgress
                            variant="determinate"
                            value={cc.budget_amount > 0 ? Math.min((cc.actual_amount / cc.budget_amount) * 100, 100) : 0}
                            color={cc.actual_amount > cc.budget_amount ? 'error' : 'primary'}
                          />
                          <Typography variant="caption" color="textSecondary">
                            {cc.budget_amount > 0 
                              ? `${((cc.actual_amount / cc.budget_amount) * 100).toFixed(0)}% of budget`
                              : 'No budget set'
                            }
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Underutilized Budgets */}
        {metrics.underutilized.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Underutilized Budgets
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Cost centers spending less than 50% of allocated budget
                </Typography>

                <Grid container spacing={2}>
                  {metrics.underutilized.map((cc) => (
                    <Grid item xs={12} sm={6} md={4} key={cc.id}>
                      <Paper sx={{ p: 2 }}>
                        <Typography variant="subtitle2" fontWeight="600">
                          {cc.cost_center_name}
                        </Typography>
                        <Box display="flex" justifyContent="space-between" mt={1}>
                          <Typography variant="caption" color="textSecondary">
                            Spent: {formatCurrency(cc.actual_amount)}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            Budget: {formatCurrency(cc.budget_amount)}
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={cc.budget_amount > 0 ? (cc.actual_amount / cc.budget_amount) * 100 : 0}
                          color="warning"
                          sx={{ mt: 1 }}
                        />
                        <Typography variant="caption" color="warning.main" mt={0.5} display="block">
                          {cc.budget_amount > 0 
                            ? `${((cc.actual_amount / cc.budget_amount) * 100).toFixed(0)}% utilized`
                            : 'N/A'
                          }
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </DashboardLayout>
    </ProtectedPage>
  );
};
export default CostAnalysisPage;