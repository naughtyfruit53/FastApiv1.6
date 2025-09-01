// pages/hr/dashboard.tsx
// HR Dashboard with key metrics and overview
import React, { useState, useEffect } from 'react';
import { NextPage } from 'next';
import { Box, Typography, Grid, Card, CardContent, Chip, Tab, Tabs, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button } from '@mui/material';
import {
  People as PeopleIcon,
  PersonAdd as PersonAddIcon,
  AccessTime as AccessTimeIcon,
  Assessment as AssessmentIcon,
  Approval as ApprovalIcon,
  Schedule as ScheduleIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useRouter } from 'next/router';
import { useAuth } from '../../hooks/useAuth';
import { hrService, HRDashboardData, HRActivity, HRTask } from '../../services';
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
      id={`hr-tabpanel-${index}`}
      aria-labelledby={`hr-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}
function a11yProps(index: number) {
  return {
    id: `hr-tab-${index}`,
    'aria-controls': `hr-tabpanel-${index}`,
  };
}
const HRDashboard: NextPage = () => {
  const router = useRouter();
const { _user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [dashboardData, setDashboardData] = useState<HRDashboardData | null>(null);
  const [recentActivities, setRecentActivities] = useState<HRActivity[]>([]);
  const [upcomingTasks, setUpcomingTasks] = useState<HRTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    fetchDashboardData();
  }, []);
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [dashboard, activities, tasks] = await Promise.all([
        hrService.getDashboardData(),
        hrService.getRecentActivities(5),
        hrService.getUpcomingTasks(5)
      ]);
      setDashboardData(dashboard);
      setRecentActivities(activities);
      setUpcomingTasks(tasks);
    } catch (err: any) {
      console.error('Error fetching HR dashboard data:', err);
      setError(err.userMessage || 'Failed to load dashboard data');
      // Fallback to empty data structure to prevent crashes
      setDashboardData({
        total_employees: 0,
        active_employees: 0,
        employees_on_leave: 0,
        pending_leave_approvals: 0,
        upcoming_performance_reviews: 0,
        recent_joiners: 0,
        employees_in_probation: 0,
        average_attendance_rate: 0,
      });
      setRecentActivities([]);
      setUpcomingTasks([]);
    } finally {
      setLoading(false);
    }
  };
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'warning';
      case 'completed':
      case 'active':
        return 'success';
      case 'rejected':
        return 'error';
      default:
        return 'default';
    }
  };
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          HR Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button 
            variant="outlined" 
            startIcon={<PersonAddIcon />}
            onClick={() => router.push('/hr/employees')}
          >
            Manage Employees
          </Button>
          <Button 
            variant="contained" 
            startIcon={<AssessmentIcon />}
            onClick={() => router.push('/hr/reports')}
          >
            HR Reports
          </Button>
        </Box>
      </Box>
      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
          <Button size="small" onClick={fetchDashboardData} sx={{ ml: 1 }}>
            Retry
          </Button>
        </Alert>
      )}
      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Employees
                  </Typography>
                  <Typography variant="h4">
                    {loading ? <CircularProgress size={24} /> : dashboardData?.total_employees || 0}
                  </Typography>
                </Box>
                <PeopleIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Employees
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {loading ? <CircularProgress size={24} /> : dashboardData?.active_employees || 0}
                  </Typography>
                </Box>
                <TrendingUpIcon color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    On Leave Today
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {loading ? <CircularProgress size={24} /> : dashboardData?.employees_on_leave || 0}
                  </Typography>
                </Box>
                <AccessTimeIcon color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Pending Approvals
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {loading ? <CircularProgress size={24} /> : dashboardData?.pending_leave_approvals || 0}
                  </Typography>
                </Box>
                <ApprovalIcon color="error" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Additional Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Recent Joiners (30 days)
              </Typography>
              <Typography variant="h5">
                {dashboardData?.recent_joiners || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                In Probation
              </Typography>
              <Typography variant="h5">
                {dashboardData?.employees_in_probation || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Upcoming Reviews
              </Typography>
              <Typography variant="h5">
                {dashboardData?.upcoming_performance_reviews || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg. Attendance
              </Typography>
              <Typography variant="h5" color="primary">
                {dashboardData?.average_attendance_rate || 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Tabs for detailed sections */}
      <Paper sx={{ width: '100%', mb: 4 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="HR dashboard tabs">
            <Tab label="Recent Activities" {...a11yProps(0)} />
            <Tab label="Upcoming Tasks" {...a11yProps(1)} />
            <Tab label="Quick Actions" {...a11yProps(2)} />
          </Tabs>
        </Box>
        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" gutterBottom>
            Recent HR Activities
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Employee</TableCell>
                  <TableCell>Activity</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recentActivities.map((activity) => (
                  <TableRow key={activity.id}>
                    <TableCell>{activity.employee}</TableCell>
                    <TableCell>{activity.action}</TableCell>
                    <TableCell>{activity.date}</TableCell>
                    <TableCell>
                      <Chip 
                        label={activity.status} 
                        color={getStatusColor(activity.status) as any}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            Upcoming HR Tasks
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Task</TableCell>
                  <TableCell>Due Date</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Category</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {upcomingTasks.map((task) => (
                  <TableRow key={task.id}>
                    <TableCell>{task.task}</TableCell>
                    <TableCell>{task.due_date}</TableCell>
                    <TableCell>
                      <Chip 
                        label={task.priority} 
                        color={getPriorityColor(task.priority) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{task.category}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            Quick Actions
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={4}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<PersonAddIcon />}
                onClick={() => router.push('/hr/employees/new')}
                sx={{ py: 2 }}
              >
                Add New Employee
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<ApprovalIcon />}
                onClick={() => router.push('/hr/leaves/approvals')}
                sx={{ py: 2 }}
              >
                Review Leave Applications
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<ScheduleIcon />}
                onClick={() => router.push('/hr/attendance')}
                sx={{ py: 2 }}
              >
                Attendance Management
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<AssessmentIcon />}
                onClick={() => router.push('/hr/performance')}
                sx={{ py: 2 }}
              >
                Performance Reviews
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<TrendingUpIcon />}
                onClick={() => router.push('/hr/reports')}
                sx={{ py: 2 }}
              >
                Generate Reports
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<WarningIcon />}
                onClick={() => router.push('/hr/settings')}
                sx={{ py: 2 }}
              >
                HR Settings
              </Button>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>
      {/* Alerts and Notifications */}
      <Box sx={{ mb: 4 }}>
        <Alert severity="info" sx={{ mb: 2 }}>
          You have {dashboardData?.pending_leave_approvals || 0} pending leave applications that require your attention.
        </Alert>
        {(dashboardData?.employees_in_probation || 0) > 0 && (
          <Alert severity="warning">
            {dashboardData?.employees_in_probation || 0} employees are currently in their probation period. 
            Review their progress and schedule confirmation meetings.
          </Alert>
        )}
      </Box>
    </Container>
  );
};
export default HRDashboard;