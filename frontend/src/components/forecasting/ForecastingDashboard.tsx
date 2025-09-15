/**
 * Forecasting Dashboard - Main dashboard for ML forecasting and predictive analytics
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  BarChart,
  Bar,
} from 'recharts';
import {
  Brain,
  TrendingUp,
  AlertTriangle,
  Target,
  Plus,
  Eye,
  Settings,
  Lightbulb,
} from 'lucide-react';
import { forecastingApi, ForecastDashboard } from '@/services/api/forecasting';

interface ForecastMetrics {
  total_forecasts: number;
  active_models: number;
  accuracy_average: number;
  predictions_this_month: number;
}

export const ForecastingDashboard: React.FC = () => {
  const [dashboard, setDashboard] = useState<ForecastDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const dashboardData = await forecastingApi.getForecastDashboard();
      setDashboard(dashboardData);
      setError(null);
    } catch (err) {
      console.error('Failed to load forecasting dashboard:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const generateInsights = async () => {
    try {
      await forecastingApi.generateInsights(['financial_forecasts', 'general_ledger'], 30);
      // Reload dashboard to show new insights
      loadDashboardData();
    } catch (err) {
      console.error('Failed to generate insights:', err);
    }
  };

  // Mock data for charts if dashboard is not loaded
  const mockPredictionData = [
    { date: '2024-01', actual: 100, predicted: 98, confidence_lower: 90, confidence_upper: 106 },
    { date: '2024-02', actual: 110, predicted: 108, confidence_lower: 100, confidence_upper: 116 },
    { date: '2024-03', actual: 105, predicted: 107, confidence_lower: 99, confidence_upper: 115 },
    { date: '2024-04', actual: 120, predicted: 118, confidence_lower: 110, confidence_upper: 126 },
    { date: '2024-05', actual: null, predicted: 125, confidence_lower: 117, confidence_upper: 133 },
    { date: '2024-06', actual: null, predicted: 130, confidence_lower: 122, confidence_upper: 138 },
  ];

  const mockAccuracyData = [
    { model: 'Revenue Forecast', accuracy: 92, mape: 8 },
    { model: 'Expense Forecast', accuracy: 88, mape: 12 },
    { model: 'Cash Flow', accuracy: 85, mape: 15 },
    { model: 'Customer Growth', accuracy: 90, mape: 10 },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Forecasting & Predictive Analytics</h1>
          <p className="text-gray-600">ML-powered forecasting, risk analysis, and automated insights</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={generateInsights}>
            <Lightbulb className="h-4 w-4 mr-2" />
            Generate Insights
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Forecast
          </Button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2 text-red-700">
          <AlertTriangle className="h-5 w-5" />
          {error}
        </div>
      )}

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Brain className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Forecasts</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboard?.active_forecasts || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <Target className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg Accuracy</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboard?.forecast_accuracy_avg || 0}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">ML Models</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboard?.performance_metrics?.total_ml_models || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Risk Alerts</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboard?.risk_alerts?.length || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Prediction Accuracy Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Forecast vs Actual Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={mockPredictionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="confidence_upper"
                  stroke="none"
                  fill="#E0E7FF"
                  fillOpacity={0.3}
                />
                <Area
                  type="monotone"
                  dataKey="confidence_lower"
                  stroke="none"
                  fill="#FFFFFF"
                  fillOpacity={1}
                />
                <Line
                  type="monotone"
                  dataKey="actual"
                  stroke="#10B981"
                  strokeWidth={2}
                  name="Actual"
                />
                <Line
                  type="monotone"
                  dataKey="predicted"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  name="Predicted"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Model Accuracy */}
        <Card>
          <CardHeader>
            <CardTitle>Model Accuracy by Type</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={mockAccuracyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="model" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="accuracy" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Key Insights and Risk Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Key Insights */}
        <Card>
          <CardHeader>
            <CardTitle>AI-Generated Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dashboard?.key_insights?.slice(0, 5).map((insight, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <div className="p-1 bg-blue-100 rounded">
                    <Lightbulb className="h-4 w-4 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-sm">{insight.title}</h4>
                    <p className="text-xs text-gray-600 mt-1">
                      Confidence: {insight.confidence_score}% | Importance: {insight.importance_score}/10
                    </p>
                  </div>
                  <Button variant="ghost" size="sm">
                    <Eye className="h-4 w-4" />
                  </Button>
                </div>
              )) || (
                <div className="text-center text-gray-500 py-8">
                  <Lightbulb className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                  <p>No insights generated yet</p>
                  <Button variant="outline" size="sm" className="mt-2" onClick={generateInsights}>
                    Generate Insights
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Risk Alerts */}
        <Card>
          <CardHeader>
            <CardTitle>Risk Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dashboard?.risk_alerts?.slice(0, 5).map((alert, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-red-50 rounded-lg">
                  <div className="p-1 bg-red-100 rounded">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-sm">{alert.risk_name}</h4>
                    <div className="flex gap-2 mt-1">
                      <Badge variant={alert.alert_level === 'critical' ? 'destructive' : 'secondary'}>
                        {alert.alert_level}
                      </Badge>
                      <span className="text-xs text-gray-600">
                        Risk Score: {alert.risk_score}/10
                      </span>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">
                    <Settings className="h-4 w-4" />
                  </Button>
                </div>
              )) || (
                <div className="text-center text-gray-500 py-8">
                  <AlertTriangle className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                  <p>No active risk alerts</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Predictions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Predictions</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Model</TableHead>
                <TableHead>Predicted Value</TableHead>
                <TableHead>Confidence</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {dashboard?.recent_predictions?.map((prediction, index) => (
                <TableRow key={index}>
                  <TableCell>
                    {new Date(prediction.prediction_date).toLocaleDateString()}
                  </TableCell>
                  <TableCell>{prediction.model_name || 'Revenue Forecast'}</TableCell>
                  <TableCell>
                    ${prediction.predicted_value?.toLocaleString() || 'N/A'}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {prediction.confidence_score || 85}%
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="default">Active</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              )) || (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-gray-500 py-8">
                    No recent predictions available
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};