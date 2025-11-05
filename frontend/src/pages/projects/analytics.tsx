// frontend/src/pages/projects/analytics.tsx
import React, { useState, useEffect } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
} from "@mui/material";
import {
  TrendingUp,
  TrendingDown,
  Assignment,
  AttachMoney,
  Schedule,
  Download,
  Refresh,
} from "@mui/icons-material";
import { Bar, Line, Doughnut } from "react-chartjs-2";
import { ProtectedPage } from "../../components/ProtectedPage";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
} from "chart.js";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
);

// Types
interface ProjectAnalytics {
  overview: {
    total_projects: number;
    active_projects: number;
    completed_projects: number;
    total_budget: number;
    budget_utilized: number;
    budget_remaining: number;
    average_completion_rate: number;
    on_time_delivery_rate: number;
  };
  performance_metrics: {
    project_id: number;
    project_name: string;
    budget_variance: number;
    schedule_variance: number;
    cost_performance_index: number;
    schedule_performance_index: number;
    earned_value: number;
    actual_cost: number;
    planned_value: number;
  }[];
  resource_utilization: {
    resource_name: string;
    resource_type: string;
    utilization_percentage: number;
    allocated_hours: number;
    actual_hours: number;
    cost_per_hour: number;
    total_cost: number;
  }[];
  project_status_distribution: {
    status: string;
    count: number;
    percentage: number;
  }[];
  budget_analysis: {
    month: string;
    planned_budget: number;
    actual_spend: number;
    variance: number;
  }[];
  timeline_analysis: {
    project_name: string;
    planned_duration: number;
    actual_duration: number;
    variance_days: number;
    completion_percentage: number;
  }[];
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analytics-tabpanel-${index}`}
      aria-labelledby={`analytics-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ProjectAnalyticsPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [analytics, setAnalytics] = useState<ProjectAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState("last_6_months");

  useEffect(() => {
    loadAnalytics();
  }, [timeRange]);

  const loadAnalytics = () => {
    setLoading(true);
    
    // Mock analytics data
    const mockAnalytics: ProjectAnalytics = {
      overview: {
        total_projects: 24,
        active_projects: 8,
        completed_projects: 14,
        total_budget: 2500000,
        budget_utilized: 1850000,
        budget_remaining: 650000,
        average_completion_rate: 78.5,
        on_time_delivery_rate: 85.7
      },
      performance_metrics: [
        {
          project_id: 1,
          project_name: "ERP Implementation",
          budget_variance: -15000,
          schedule_variance: 5,
          cost_performance_index: 1.08,
          schedule_performance_index: 0.95,
          earned_value: 125000,
          actual_cost: 115000,
          planned_value: 130000
        },
        {
          project_id: 2,
          project_name: "Mobile App Development",
          budget_variance: 8000,
          schedule_variance: -12,
          cost_performance_index: 0.92,
          schedule_performance_index: 1.15,
          earned_value: 85000,
          actual_cost: 92000,
          planned_value: 75000
        },
        {
          project_id: 3,
          project_name: "Cloud Migration",
          budget_variance: -2500,
          schedule_variance: 2,
          cost_performance_index: 1.05,
          schedule_performance_index: 0.98,
          earned_value: 65000,
          actual_cost: 62000,
          planned_value: 66000
        }
      ],
      resource_utilization: [
        {
          resource_name: "Senior Developer",
          resource_type: "human",
          utilization_percentage: 92,
          allocated_hours: 160,
          actual_hours: 147,
          cost_per_hour: 85,
          total_cost: 12495
        },
        {
          resource_name: "Project Manager",
          resource_type: "human",
          utilization_percentage: 78,
          allocated_hours: 120,
          actual_hours: 94,
          cost_per_hour: 95,
          total_cost: 8930
        },
        {
          resource_name: "Business Analyst",
          resource_type: "human",
          utilization_percentage: 85,
          allocated_hours: 100,
          actual_hours: 85,
          cost_per_hour: 75,
          total_cost: 6375
        }
      ],
      project_status_distribution: [
        { status: "active", count: 8, percentage: 33.3 },
        { status: "completed", count: 14, percentage: 58.3 },
        { status: "on_hold", count: 1, percentage: 4.2 },
        { status: "cancelled", count: 1, percentage: 4.2 }
      ],
      budget_analysis: [
        { month: "Jan 2024", planned_budget: 200000, actual_spend: 185000, variance: -15000 },
        { month: "Feb 2024", planned_budget: 220000, actual_spend: 235000, variance: 15000 },
        { month: "Mar 2024", planned_budget: 180000, actual_spend: 175000, variance: -5000 },
        { month: "Apr 2024", planned_budget: 250000, actual_spend: 240000, variance: -10000 },
        { month: "May 2024", planned_budget: 300000, actual_spend: 320000, variance: 20000 },
        { month: "Jun 2024", planned_budget: 280000, actual_spend: 275000, variance: -5000 }
      ],
      timeline_analysis: [
        {
          project_name: "ERP Implementation",
          planned_duration: 180,
          actual_duration: 165,
          variance_days: -15,
          completion_percentage: 85
        },
        {
          project_name: "Mobile App Development",
          planned_duration: 120,
          actual_duration: 140,
          variance_days: 20,
          completion_percentage: 95
        },
        {
          project_name: "Cloud Migration",
          planned_duration: 90,
          actual_duration: 85,
          variance_days: -5,
          completion_percentage: 100
        }
      ]
    };

    setTimeout(() => {
      setAnalytics(mockAnalytics);
      setLoading(false);
    }, 1000);
  };

  const getVarianceColor = (variance: number) => {
    if (variance > 0) return 'error';
    if (variance < 0) return 'success';
    return 'default';
  };

  const getVarianceIcon = (variance: number) => {
    if (variance > 0) return <TrendingUp color="error" />;
    if (variance < 0) return <TrendingDown color="success" />;
    return null;
  };

  // Chart configurations
  const statusDistributionData = analytics ? {
    labels: analytics.project_status_distribution.map(item => item.status.replace('_', ' ')),
    datasets: [
      {
        data: analytics.project_status_distribution.map(item => item.count),
        backgroundColor: [
          '#4caf50', // active - green
          '#2196f3', // completed - blue
          '#ff9800', // on_hold - orange
          '#f44336', // cancelled - red
        ],
        borderWidth: 2,
      },
    ],
  } : null;

  const budgetAnalysisData = analytics ? {
    labels: analytics.budget_analysis.map(item => item.month),
    datasets: [
      {
        label: 'Planned Budget',
        data: analytics.budget_analysis.map(item => item.planned_budget),
        borderColor: '#2196f3',
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Actual Spend',
        data: analytics.budget_analysis.map(item => item.actual_spend),
        borderColor: '#ff9800',
        backgroundColor: 'rgba(255, 152, 0, 0.1)',
        tension: 0.4,
      },
    ],
  } : null;

  const resourceUtilizationData = analytics ? {
    labels: analytics.resource_utilization.map(item => item.resource_name),
    datasets: [
      {
        label: 'Utilization %',
        data: analytics.resource_utilization.map(item => item.utilization_percentage),
        backgroundColor: [
          'rgba(76, 175, 80, 0.8)',
          'rgba(33, 150, 243, 0.8)',
          'rgba(255, 193, 7, 0.8)',
        ],
        borderColor: [
          '#4caf50',
          '#2196f3',
          '#ffc107',
        ],
        borderWidth: 2,
      },
    ],
  } : null;

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <ProtectedPage moduleKey="projects" action="read">
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Project Analytics
        </Typography>
        <Stack direction="row" spacing={2} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value as string)}
            >
              <MenuItem value="last_3_months">Last 3 Months</MenuItem>
              <MenuItem value="last_6_months">Last 6 Months</MenuItem>
              <MenuItem value="last_year">Last Year</MenuItem>
              <MenuItem value="all_time">All Time</MenuItem>
            </Select>
          </FormControl>
          <Button startIcon={<Refresh />} onClick={loadAnalytics}>
            Refresh
          </Button>
          <Button startIcon={<Download />} variant="outlined">
            Export
          </Button>
        </Stack>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Overview Cards */}
      {analytics && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Assignment sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Projects
                    </Typography>
                    <Typography variant="h4">
                      {analytics.overview.total_projects}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <AttachMoney sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Budget
                    </Typography>
                    <Typography variant="h4">
                      ${(analytics.overview.total_budget / 1000000).toFixed(1)}M
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <TrendingUp sx={{ fontSize: 40, color: 'info.main', mr: 2 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Avg Completion
                    </Typography>
                    <Typography variant="h4">
                      {analytics.overview.average_completion_rate}%
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Schedule sx={{ fontSize: 40, color: 'warning.main', mr: 2 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      On-Time Delivery
                    </Typography>
                    <Typography variant="h4">
                      {analytics.overview.on_time_delivery_rate}%
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Paper sx={{ width: '100%' }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Overview" />
          <Tab label="Performance" />
          <Tab label="Resources" />
          <Tab label="Timeline" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            {/* Status Distribution */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Project Status Distribution
                  </Typography>
                  {statusDistributionData && (
                    <Box sx={{ height: 300, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                      <Doughnut data={statusDistributionData} options={{ maintainAspectRatio: false }} />
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Budget Analysis */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Budget Analysis Trend
                  </Typography>
                  {budgetAnalysisData && (
                    <Box sx={{ height: 300 }}>
                      <Line data={budgetAnalysisData} options={{ maintainAspectRatio: false }} />
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Resource Utilization */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Resource Utilization
                  </Typography>
                  {resourceUtilizationData && (
                    <Box sx={{ height: 300 }}>
                      <Bar data={resourceUtilizationData} options={{ maintainAspectRatio: false }} />
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {/* Performance Metrics */}
          <Typography variant="h6" gutterBottom>
            Project Performance Metrics
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Project Name</TableCell>
                  <TableCell>Budget Variance</TableCell>
                  <TableCell>Schedule Variance</TableCell>
                  <TableCell>Cost Performance Index</TableCell>
                  <TableCell>Schedule Performance Index</TableCell>
                  <TableCell>Earned Value</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {analytics?.performance_metrics.map((metric) => (
                  <TableRow key={metric.project_id} hover>
                    <TableCell>{metric.project_name}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getVarianceIcon(metric.budget_variance)}
                        <Chip
                          label={`$${Math.abs(metric.budget_variance).toLocaleString()}`}
                          color={getVarianceColor(metric.budget_variance) as any}
                          size="small"
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getVarianceIcon(metric.schedule_variance)}
                        <Chip
                          label={`${Math.abs(metric.schedule_variance)} days`}
                          color={getVarianceColor(metric.schedule_variance) as any}
                          size="small"
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={metric.cost_performance_index.toFixed(2)}
                        color={metric.cost_performance_index >= 1 ? 'success' : 'warning'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={metric.schedule_performance_index.toFixed(2)}
                        color={metric.schedule_performance_index >= 1 ? 'success' : 'warning'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>${metric.earned_value.toLocaleString()}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {/* Resource Analysis */}
          <Typography variant="h6" gutterBottom>
            Resource Utilization Analysis
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Resource Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Utilization %</TableCell>
                  <TableCell>Allocated Hours</TableCell>
                  <TableCell>Actual Hours</TableCell>
                  <TableCell>Cost per Hour</TableCell>
                  <TableCell>Total Cost</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {analytics?.resource_utilization.map((resource, index) => (
                  <TableRow key={index} hover>
                    <TableCell>{resource.resource_name}</TableCell>
                    <TableCell>
                      <Chip label={resource.resource_type} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box sx={{ width: 60, bgcolor: 'grey.200', borderRadius: 1 }}>
                          <Box
                            sx={{
                              width: `${resource.utilization_percentage}%`,
                              height: 8,
                              bgcolor: resource.utilization_percentage >= 80 ? 'success.main' : 
                                      resource.utilization_percentage >= 60 ? 'warning.main' : 'error.main',
                              borderRadius: 1,
                            }}
                          />
                        </Box>
                        <Typography variant="body2">
                          {resource.utilization_percentage}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{resource.allocated_hours}</TableCell>
                    <TableCell>{resource.actual_hours}</TableCell>
                    <TableCell>${resource.cost_per_hour}</TableCell>
                    <TableCell>${resource.total_cost.toLocaleString()}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          {/* Timeline Analysis */}
          <Typography variant="h6" gutterBottom>
            Project Timeline Analysis
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Project Name</TableCell>
                  <TableCell>Planned Duration (days)</TableCell>
                  <TableCell>Actual Duration (days)</TableCell>
                  <TableCell>Variance (days)</TableCell>
                  <TableCell>Completion %</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {analytics?.timeline_analysis.map((timeline, index) => (
                  <TableRow key={index} hover>
                    <TableCell>{timeline.project_name}</TableCell>
                    <TableCell>{timeline.planned_duration}</TableCell>
                    <TableCell>{timeline.actual_duration}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getVarianceIcon(timeline.variance_days)}
                        <Chip
                          label={`${Math.abs(timeline.variance_days)} days`}
                          color={getVarianceColor(timeline.variance_days) as any}
                          size="small"
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box sx={{ width: 60, bgcolor: 'grey.200', borderRadius: 1 }}>
                          <Box
                            sx={{
                              width: `${timeline.completion_percentage}%`,
                              height: 8,
                              bgcolor: timeline.completion_percentage >= 80 ? 'success.main' : 
                                      timeline.completion_percentage >= 50 ? 'warning.main' : 'info.main',
                              borderRadius: 1,
                            }}
                          />
                        </Box>
                        <Typography variant="body2">
                          {timeline.completion_percentage}%
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>
      </Paper>
    </Box>
  );
  </ProtectedPage>
  );
};

export default ProjectAnalyticsPage;