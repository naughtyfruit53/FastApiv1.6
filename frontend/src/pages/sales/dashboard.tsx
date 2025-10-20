"use client";
import React, { useState, useEffect } from "react";
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Button,
  CircularProgress,
  Alert,
  Divider,
  Paper,
  Stack,
  Chip,
} from "@mui/material";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useRouter } from "next/router";
import { crmService } from "@services/crmService";

interface DashboardStats {
  totalLeads: number;
  qualifiedLeads: number;
  totalOpportunities: number;
  wonOpportunities: number;
  totalPipelineValue: number;
  avgDealSize: number;
  conversionRate: number;
}

interface LeadStatusData {
  name: string;
  count: number;
}

interface RecentActivity {
  id: number;
  type: string;
  description: string;
  created_at: string;
}

const SalesDashboard: React.FC = () => {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [leadStatusData, setLeadStatusData] = useState<LeadStatusData[]>([]);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setError("No authentication token found. Please log in.");
      setLoading(false);
      router.push("/login");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Fetch analytics data with a 30-day range
      const periodEnd = new Date();
      const periodStart = new Date(periodEnd);
      periodStart.setDate(periodEnd.getDate() - 30);
      const analytics = await crmService.getAnalytics({
        period_start: periodStart.toISOString().split('T')[0],
        period_end: periodEnd.toISOString().split('T')[0],
      });

      setStats({
        totalLeads: analytics.leads_total,
        qualifiedLeads: analytics.leads_by_status.qualified || 0,
        totalOpportunities: analytics.opportunities_total,
        wonOpportunities: analytics.opportunities_by_stage.closed_won || 0,
        totalPipelineValue: analytics.pipeline_value,
        avgDealSize: analytics.average_deal_size,
        conversionRate: analytics.conversion_rate,
      });

      // Transform lead status data for chart
      const statusData = Object.entries(analytics.leads_by_status).map(([name, count]) => ({
        name: name.replace("_", " ").toUpperCase(),
        count,
      }));
      setLeadStatusData(statusData);

      // Fetch recent activities (mock for now, replace with actual API call)
      setRecentActivities([
        {
          id: 1,
          type: "Lead Created",
          description: "New lead added: John Doe",
          created_at: new Date().toISOString(),
        },
        {
          id: 2,
          type: "Opportunity Updated",
          description: "Opportunity stage changed to Proposal",
          created_at: new Date(Date.now() - 86400000).toISOString(),
        },
      ]);
    } catch (err: any) {
      console.error("Error fetching dashboard data:", err);
      const errorMessage = err.userMessage || err.message || "Failed to load dashboard data. Please try again.";
      setError(errorMessage);
      if (err.status === 401 || err.message.includes("No authentication token") || err.message.includes("Session expired")) {
        localStorage.removeItem("access_token");
        router.push("/login");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [router]);

  const handleViewLeads = () => {
    router.push("/sales/leads");
  };

  const handleViewOpportunities = () => {
    router.push("/sales/opportunities");
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          {error}
          <Button
            variant="outlined"
            size="small"
            onClick={fetchDashboardData}
            sx={{ ml: 2 }}
          >
            Retry
          </Button>
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Sales Dashboard
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Leads
              </Typography>
              <Typography variant="h5">{stats?.totalLeads || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Qualified Leads
              </Typography>
              <Typography variant="h5" color="success.main">
                {stats?.qualifiedLeads || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Opportunities
              </Typography>
              <Typography variant="h5">{stats?.totalOpportunities || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Pipeline Value
              </Typography>
              <Typography variant="h5" color="success.main">
                ${stats?.totalPipelineValue.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Lead Status Chart */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <CardHeader title="Lead Status Distribution" />
        <Box sx={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={leadStatusData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </Paper>

      {/* Recent Activities */}
      <Paper sx={{ p: 3 }}>
        <CardHeader title="Recent Activities" />
        <Stack spacing={2}>
          {recentActivities.map((activity) => (
            <Box key={activity.id}>
              <Stack direction="row" spacing={2} alignItems="center">
                <Chip label={activity.type} color="primary" size="small" />
                <Typography variant="body2">{activity.description}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(activity.created_at).toLocaleString()}
                </Typography>
              </Stack>
              <Divider sx={{ my: 1 }} />
            </Box>
          ))}
        </Stack>
      </Paper>

      {/* Action Buttons */}
      <Box sx={{ mt: 4, display: "flex", gap: 2 }}>
        <Button variant="contained" onClick={handleViewLeads}>
          View Leads
        </Button>
        <Button variant="contained" onClick={handleViewOpportunities}>
          View Opportunities
        </Button>
      </Box>
    </Container>
  );
};

export default SalesDashboard;