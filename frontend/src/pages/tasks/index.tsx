// pages/tasks/index.tsx
import React from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Grid,
  Alert,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Checkbox,
  Fab
} from '@mui/material';
import { 
  Add, 
  Assignment,
  CheckCircle,
  Schedule,
  Flag
} from '@mui/icons-material';
import DashboardLayout from '../../components/DashboardLayout';

const TasksPage: React.FC = () => {
  const taskStats = {
    total: 24,
    completed: 18,
    pending: 4,
    overdue: 2
  };

  const recentTasks = [
    { id: 1, title: 'Complete project documentation', status: 'pending', priority: 'high', dueDate: 'Today' },
    { id: 2, title: 'Review marketing campaign', status: 'completed', priority: 'medium', dueDate: 'Yesterday' },
    { id: 3, title: 'Prepare monthly report', status: 'pending', priority: 'high', dueDate: 'Tomorrow' },
    { id: 4, title: 'Team standup meeting', status: 'completed', priority: 'low', dueDate: 'Today' },
    { id: 5, title: 'Update client requirements', status: 'overdue', priority: 'high', dueDate: '2 days ago' },
  ];

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'pending': return 'primary';
      case 'overdue': return 'error';
      default: return 'default';
    }
  };

  return (
    <DashboardLayout
      title="My Tasks"
      subtitle="Manage your tasks and track progress"
      actions={
        <Button 
          variant="contained" 
          startIcon={<Add />}
          href="/tasks/create"
        >
          New Task
        </Button>
      }
    >
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Alert severity="info" sx={{ mb: 3 }}>
            Stay organized and track your daily tasks. Set priorities and deadlines to boost productivity.
          </Alert>
        </Grid>
        
        {/* Task Statistics */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Assignment sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Total Tasks</Typography>
              </Box>
              <Typography variant="h3" color="primary.main">
                {taskStats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CheckCircle sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="h6">Completed</Typography>
              </Box>
              <Typography variant="h3" color="success.main">
                {taskStats.completed}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Schedule sx={{ mr: 1, color: 'warning.main' }} />
                <Typography variant="h6">Pending</Typography>
              </Box>
              <Typography variant="h3" color="warning.main">
                {taskStats.pending}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Flag sx={{ mr: 1, color: 'error.main' }} />
                <Typography variant="h6">Overdue</Typography>
              </Box>
              <Typography variant="h3" color="error.main">
                {taskStats.overdue}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Progress Overview */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Progress Overview
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography variant="body2" sx={{ minWidth: 120 }}>
                  Completion Rate
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={(taskStats.completed / taskStats.total) * 100}
                  sx={{ flexGrow: 1, mx: 2 }}
                />
                <Typography variant="body2">
                  {Math.round((taskStats.completed / taskStats.total) * 100)}%
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Recent Tasks */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Tasks
              </Typography>
              <List>
                {recentTasks.map((task) => (
                  <ListItem key={task.id} divider>
                    <ListItemIcon>
                      <Checkbox 
                        checked={task.status === 'completed'}
                        disabled={task.status === 'completed'}
                      />
                    </ListItemIcon>
                    <ListItemText
                      primary={task.title}
                      secondary={`Due: ${task.dueDate}`}
                    />
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Chip 
                        label={task.priority}
                        color={getPriorityColor(task.priority) as any}
                        size="small"
                      />
                      <Chip 
                        label={task.status}
                        color={getStatusColor(task.status) as any}
                        size="small"
                      />
                    </Box>
                  </ListItem>
                ))}
              </List>
              
              <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                <Button variant="outlined" href="/tasks/assignments">
                  View Assignments
                </Button>
                <Button variant="outlined" href="/tasks/templates">
                  Task Templates
                </Button>
                <Button variant="outlined" href="/tasks/reminders">
                  Manage Reminders
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Fab 
        color="primary" 
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        href="/tasks/create"
      >
        <Add />
      </Fab>
    </DashboardLayout>
  );
};

export default TasksPage;