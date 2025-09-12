/**
 * Financial Modeling Dashboard - Main dashboard for financial models and valuations
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
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import {
  Calculator,
  TrendingUp,
  DollarSign,
  Activity,
  Plus,
  FileText,
  AlertCircle,
} from 'lucide-react';
import { financialModelingApi } from '@/services/api/financial-modeling';

interface FinancialModel {
  id: number;
  model_name: string;
  model_type: string;
  model_version: string;
  is_approved: boolean;
  created_at: string;
  valuation_results: any;
}

interface DashboardMetrics {
  total_models: number;
  approved_models: number;
  dcf_models: number;
  avg_valuation: number;
  recent_models: FinancialModel[];
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export const FinancialModelingDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [models, setModels] = useState<FinancialModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load financial models
      const modelsResponse = await financialModelingApi.getFinancialModels({
        limit: 10,
        skip: 0
      });
      
      setModels(modelsResponse);
      
      // Calculate metrics
      const totalModels = modelsResponse.length;
      const approvedModels = modelsResponse.filter(m => m.is_approved).length;
      const dcfModels = modelsResponse.filter(m => m.model_type === 'dcf').length;
      
      // Calculate average valuation (simplified)
      const valuations = modelsResponse
        .filter(m => m.valuation_results?.equity_value)
        .map(m => parseFloat(m.valuation_results.equity_value));
      const avgValuation = valuations.length > 0 
        ? valuations.reduce((a, b) => a + b, 0) / valuations.length 
        : 0;

      setMetrics({
        total_models: totalModels,
        approved_models: approvedModels,
        dcf_models: dcfModels,
        avg_valuation: avgValuation,
        recent_models: modelsResponse.slice(0, 5)
      });
      
      setError(null);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const modelTypeData = models.reduce((acc, model) => {
    const type = model.model_type;
    const existing = acc.find(item => item.name === type);
    if (existing) {
      existing.value += 1;
    } else {
      acc.push({ name: type, value: 1 });
    }
    return acc;
  }, [] as Array<{ name: string; value: number }>);

  const recentActivity = models
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 6)
    .map(model => ({
      date: new Date(model.created_at).toLocaleDateString(),
      models: 1,
      type: model.model_type
    }));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-600 flex items-center gap-2">
          <AlertCircle className="h-5 w-5" />
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Financial Modeling</h1>
          <p className="text-gray-600">DCF models, valuations, and scenario analysis</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline">
            <FileText className="h-4 w-4 mr-2" />
            Templates
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Model
          </Button>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Calculator className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Models</p>
                <p className="text-2xl font-bold text-gray-900">
                  {metrics?.total_models || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Approved Models</p>
                <p className="text-2xl font-bold text-gray-900">
                  {metrics?.approved_models || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Activity className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">DCF Models</p>
                <p className="text-2xl font-bold text-gray-900">
                  {metrics?.dcf_models || 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <DollarSign className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg Valuation</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${(metrics?.avg_valuation || 0).toLocaleString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Model Types Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Model Types Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={modelTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {modelTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Model Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={recentActivity}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="models" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Models Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Financial Models</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Model Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Version</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {metrics?.recent_models.map((model) => (
                <TableRow key={model.id}>
                  <TableCell className="font-medium">
                    {model.model_name}
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary">
                      {model.model_type.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>{model.model_version}</TableCell>
                  <TableCell>
                    <Badge variant={model.is_approved ? "default" : "outline"}>
                      {model.is_approved ? "Approved" : "Draft"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {new Date(model.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        View
                      </Button>
                      <Button variant="outline" size="sm">
                        Edit
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};