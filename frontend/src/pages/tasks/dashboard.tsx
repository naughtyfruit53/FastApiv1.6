// frontend/src/pages/tasks/dashboard.tsx

'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Paper,
  LinearProgress,
  Chip,
  IconButton,
  Button
} from '@mui/material';
import {
  Task,
  Dashboard,
  TrendingUp,
  Assignment,
  Timer,
  Today,
  Warning,
  CheckCircle,
  Add
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';

interface TaskStats {
  total_tasks: number;
  todo_tasks: number;
  in_progress_tasks: number;
  review_tasks: number;
  done_tasks: number;
  cancelled_tasks: number;
  overdue_tasks: number;
  due_today_tasks: number;
  due_this_week_tasks: number;
  assigned_to_me: number;
  created_by_me: number;
}

const TaskDashboard: React.FC = () => {
  const router = useRouter();
  const [stats, setStats] = useState<TaskStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Simulate API call - replace with actual API integration
    const fetchStats = async () => {
      try {
        setLoading(true);
        // TODO: Replace with actual API call to /api/v1/tasks/dashboard
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate delay
        
        // Mock data for demonstration
        const mockStats: TaskStats = {
          total_tasks: 45,
          todo_tasks: 12,
          in_progress_tasks: 8,
          review_tasks: 3,
          done_tasks: 20,
          cancelled_tasks: 2,
          overdue_tasks: 5,
          due_today_tasks: 3,
          due_this_week_tasks: 8,
          assigned_to_me: 15,
          created_by_me: 23
        };
        
        setStats(mockStats);
      } catch (err) {
        setError('Failed to load task dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const getCompletionPercentage = (stats: TaskStats) => {
    if (stats.total_tasks === 0) {return 0;}
    return Math.round((stats.done_tasks / stats.total_tasks) * 100);
  };

  const handleNavigate = (path: string) => {
    router.push(path);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!stats) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">No task data available</Alert>
      </Box>
    );
  }

  const completionPercentage = getCompletionPercentage(stats);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Dashboard color="primary" />
          Task Management Dashboard
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleNavigate('/tasks/create')}
        >
          Create Task
        </Button>
      </Box>

      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Tasks
                  </Typography>
                  <Typography variant="h5">
                    {stats.total_tasks}
                  </Typography>
                </Box>
                <Task color="primary" sx={{ fontSize: 40 }} />
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
                    Assigned to Me
                  </Typography>
                  <Typography variant="h5">
                    {stats.assigned_to_me}
                  </Typography>
                </Box>
                <Assignment color="info" sx={{ fontSize: 40 }} />
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
                    Overdue Tasks
                  </Typography>
                  <Typography variant="h5" color={stats.overdue_tasks > 0 ? "error" : "textPrimary"}>
                    {stats.overdue_tasks}
                  </Typography>
                </Box>
                <Warning color={stats.overdue_tasks > 0 ? "error" : "disabled"} sx={{ fontSize: 40 }} />
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
                    Completion Rate
                  </Typography>
                  <Typography variant="h5" color="success.main">
                    {completionPercentage}%
                  </Typography>
                </Box>
                <CheckCircle color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Task Status Breakdown */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Task Status Breakdown
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">To Do</Typography>
                  <Typography variant="body2">{stats.todo_tasks}</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={stats.total_tasks > 0 ? (stats.todo_tasks / stats.total_tasks) * 100 : 0}
                  sx={{ mb: 2, height: 8, borderRadius: 1 }}
                />

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">In Progress</Typography>
                  <Typography variant="body2">{stats.in_progress_tasks}</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={stats.total_tasks > 0 ? (stats.in_progress_tasks / stats.total_tasks) * 100 : 0}
                  color="warning"
                  sx={{ mb: 2, height: 8, borderRadius: 1 }}
                />

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Review</Typography>
                  <Typography variant="body2">{stats.review_tasks}</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={stats.total_tasks > 0 ? (stats.review_tasks / stats.total_tasks) * 100 : 0}
                  color="info"
                  sx={{ mb: 2, height: 8, borderRadius: 1 }}
                />

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Done</Typography>
                  <Typography variant="body2">{stats.done_tasks}</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={stats.total_tasks > 0 ? (stats.done_tasks / stats.total_tasks) * 100 : 0}
                  color="success"
                  sx={{ mb: 2, height: 8, borderRadius: 1 }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                <Button
                  variant="outlined"
                  startIcon={<Task />}
                  onClick={() => handleNavigate('/tasks')}
                  fullWidth
                >
                  View All Tasks
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Assignment />}
                  onClick={() => handleNavigate('/tasks/projects')}
                  fullWidth
                >
                  Manage Projects
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Timer />}
                  onClick={() => handleNavigate('/tasks/time-logs')}
                  fullWidth
                >
                  Time Tracking
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<TrendingUp />}
                  onClick={() => handleNavigate('/tasks/reports')}
                  fullWidth
                >
                  Task Reports
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Upcoming Deadlines */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Today color="primary" />
                Due Today
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip
                  label={`${stats.due_today_tasks} tasks`}
                  color={stats.due_today_tasks > 0 ? "warning" : "default"}
                  size="small"
                />
                {stats.due_today_tasks > 0 && (
                  <Button
                    size="small"
                    onClick={() => handleNavigate('/tasks?filter=due_today')}
                  >
                    View Tasks
                  </Button>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Timer color="primary" />
                Due This Week
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip
                  label={`${stats.due_this_week_tasks} tasks`}
                  color={stats.due_this_week_tasks > 0 ? "info" : "default"}
                  size="small"
                />
                {stats.due_this_week_tasks > 0 && (
                  <Button
                    size="small"
                    onClick={() => handleNavigate('/tasks?filter=due_this_week')}
                  >
                    View Tasks
                  </Button>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TaskDashboard;