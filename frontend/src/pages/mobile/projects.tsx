import React, { useState } from 'react';
import { Box, Grid, Typography, Chip, List, ListItem, ListItemIcon, ListItemText, LinearProgress } from '@mui/material';
import { 
  Assignment, 
  Schedule, 
  People, 
  TrendingUp, 
  CheckCircle, 
  Warning, 
  Add,
  Analytics,
  Timeline,
  AttachMoney,
  CalendarToday,
  Group
} from '@mui/icons-material';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton, 
  MobileTable,
  MobileSearchBar,
  MobilePullToRefresh,
  MobileBottomSheet,
  MobileContextualActions,
  createStandardActions
} from '../../components/mobile';
import { useMobileDetection } from '../../hooks/useMobileDetection';
import ModernLoading from "../../components/ModernLoading";

// Mock data - TODO: Replace with real API integration
const mockProjects = [
  {
    id: 1,
    name: 'ERP System Upgrade',
    status: 'in_progress',
    progress: 68,
    budget: 50000,
    spent: 34000,
    team_size: 5,
    deadline: '2024-03-15',
    priority: 'high',
    manager: 'John Smith'
  },
  {
    id: 2,
    name: 'Mobile App Development',
    status: 'planning',
    progress: 15,
    budget: 30000,
    spent: 4500,
    team_size: 3,
    deadline: '2024-04-30',
    priority: 'medium',
    manager: 'Sarah Johnson'
  },
  {
    id: 3,
    name: 'Data Migration Project',
    status: 'completed',
    progress: 100,
    budget: 20000,
    spent: 18500,
    team_size: 4,
    deadline: '2024-01-30',
    priority: 'high',
    manager: 'Mike Davis'
  }
];

const mockMetrics = {
  total_projects: 15,
  active_projects: 8,
  completed_projects: 4,
  on_budget_projects: 12,
  avg_completion: 67.5,
  total_budget: 450000,
  total_spent: 298000,
  team_utilization: 87.3
};

// Define mobile-optimized table columns for projects
const projectColumns = [
  {
    key: 'name',
    label: 'Project',
    render: (value: string, row: any) => (
      <Box>
        <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
          {value}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {row.manager} • {row.team_size} members
        </Typography>
      </Box>
    ),
  },
  {
    key: 'progress',
    label: 'Progress',
    render: (value: number, row: any) => (
      <Box sx={{ minWidth: 80 }}>
        <Typography variant="caption" sx={{ fontWeight: 600 }}>
          {value}%
        </Typography>
        <LinearProgress 
          variant="determinate" 
          value={value} 
          sx={{ 
            mt: 0.5,
            height: 4,
            borderRadius: 2,
            backgroundColor: 'grey.200',
            '& .MuiLinearProgress-bar': {
              borderRadius: 2,
              backgroundColor: value >= 90 ? 'success.main' : value >= 50 ? 'primary.main' : 'warning.main'
            }
          }} 
        />
      </Box>
    ),
  },
  {
    key: 'status',
    label: 'Status',
    render: (value: string) => (
      <Chip
        label={value.replace('_', ' ').charAt(0).toUpperCase() + value.replace('_', ' ').slice(1)}
        size="small"
        color={
          value === 'completed' ? 'success' 
          : value === 'in_progress' ? 'primary'
          : value === 'planning' ? 'warning' 
          : value === 'on_hold' ? 'error'
          : 'default'
        }
        sx={{ fontSize: '0.75rem' }}
      />
    ),
  },
];

const MobileProjects: React.FC = () => {
  const [localSearchQuery, setLocalSearchQuery] = useState('');
  const [quickActionsOpen, setQuickActionsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const { isMobile } = useMobileDetection();

  const handleRefresh = async () => {
    setRefreshing(true);
    // TODO: Implement real refresh logic
    await new Promise(resolve => setTimeout(resolve, 1000));
    setRefreshing(false);
  };

  const handleSearch = (query: string) => {
    setLocalSearchQuery(query);
    // TODO: Implement real search logic
  };

  // Contextual actions for projects
  const contextualActions = createStandardActions.crud({
    onCreate: () => setQuickActionsOpen(true),
  }).concat([
    {
      icon: <Analytics />,
      name: 'Analytics',
      onClick: () => console.log('View project analytics'),
      color: 'info' as const
    },
    {
      icon: <Timeline />,
      name: 'Timeline',
      onClick: () => console.log('View project timeline'),
      color: 'secondary' as const
    }
  ]);

  const rightActions = (
    <MobileButton
      variant="contained"
      startIcon={<Add />}
      size="small"
      onClick={() => setQuickActionsOpen(true)}
    >
      Project
    </MobileButton>
  );

  if (loading) {
    return (
      <MobileDashboardLayout
        title="Projects"
        subtitle="Project management"
        rightActions={rightActions}
        showBottomNav={true}
      >
        <ModernLoading
          type="skeleton"
          skeletonType="dashboard"
          count={6}
          message="Loading project data..."
        />
      </MobileDashboardLayout>
    );
  }

  return (
    <MobileDashboardLayout
      title="Projects"
      subtitle="Project management"
      rightActions={rightActions}
      showBottomNav={true}
    >
      <MobilePullToRefresh
        onRefresh={handleRefresh}
        isRefreshing={refreshing}
        enabled={true}
      >
        {/* Search and Filter */}
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <Box sx={{ flex: 1 }}>
            <MobileSearchBar
              value={localSearchQuery}
              onChange={handleSearch}
              placeholder="Search projects..."
            />
          </Box>
        </Box>

        {/* Project Metrics */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={4}>
            <MobileCard>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                  <Assignment sx={{ fontSize: '1.5rem', color: 'primary.main' }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main' }}>
                  {mockMetrics.total_projects}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total Projects
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', color: 'success.main' }}>
                  {mockMetrics.active_projects} active
                </Typography>
              </Box>
            </MobileCard>
          </Grid>
          <Grid item xs={4}>
            <MobileCard>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                  <TrendingUp sx={{ fontSize: '1.5rem', color: 'success.main' }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'success.main' }}>
                  {mockMetrics.avg_completion}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Avg Progress
                </Typography>
                <Typography variant="caption" sx={{ display: 'block' }}>
                  {mockMetrics.completed_projects} completed
                </Typography>
              </Box>
            </MobileCard>
          </Grid>
          <Grid item xs={4}>
            <MobileCard>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                  <AttachMoney sx={{ fontSize: '1.5rem', color: 'warning.main' }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'warning.main' }}>
                  {((mockMetrics.total_spent / mockMetrics.total_budget) * 100).toFixed(0)}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Budget Used
                </Typography>
                <Typography variant="caption" sx={{ display: 'block' }}>
                  ${mockMetrics.total_spent.toLocaleString()}
                </Typography>
              </Box>
            </MobileCard>
          </Grid>
        </Grid>

        {/* Team Utilization */}
        <MobileCard title="Team Utilization">
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">Team Capacity</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {mockMetrics.team_utilization}%
              </Typography>
            </Box>
            <LinearProgress 
              variant="determinate" 
              value={mockMetrics.team_utilization} 
              sx={{ 
                height: 8, 
                borderRadius: 4,
                backgroundColor: 'grey.200',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 4,
                  backgroundColor: mockMetrics.team_utilization >= 90 ? 'error.main' : 
                                 mockMetrics.team_utilization >= 70 ? 'warning.main' : 'success.main'
                }
              }} 
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              {mockMetrics.team_utilization >= 90 ? 'Over-utilized - Consider resource reallocation' :
               mockMetrics.team_utilization >= 70 ? 'Well-utilized team capacity' :
               'Team has available capacity'}
            </Typography>
          </Box>
        </MobileCard>

        {/* Active Projects */}
        <MobileCard title="Active Projects">
          <MobileTable
            columns={projectColumns}
            data={mockProjects}
            onRowClick={(row) => console.log('Project clicked:', row)}
            showChevron={true}
            emptyMessage="No projects found"
          />
        </MobileCard>

        {/* Quick Actions */}
        <MobileCard title="Quick Actions">
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <MobileButton 
                variant="outlined" 
                fullWidth
                startIcon={<Add />}
                onClick={() => setQuickActionsOpen(true)}
              >
                New Project
              </MobileButton>
            </Grid>
            <Grid item xs={6}>
              <MobileButton 
                variant="outlined" 
                fullWidth
                startIcon={<Analytics />}
                onClick={() => console.log('Project analytics')}
              >
                Analytics
              </MobileButton>
            </Grid>
            <Grid item xs={6}>
              <MobileButton 
                variant="outlined" 
                fullWidth
                startIcon={<Timeline />}
                onClick={() => console.log('Project timeline')}
              >
                Timeline
              </MobileButton>
            </Grid>
            <Grid item xs={6}>
              <MobileButton 
                variant="outlined" 
                fullWidth
                startIcon={<Group />}
                onClick={() => console.log('Team management')}
              >
                Teams
              </MobileButton>
            </Grid>
          </Grid>
        </MobileCard>

        {/* TODO: Future implementations */}
        {/* TODO: Integrate with projectService APIs */}
        {/* TODO: Add Gantt chart for mobile */}
        {/* TODO: Implement resource allocation interface */}
        {/* TODO: Add project timeline view */}
        {/* TODO: Implement task management */}
        {/* TODO: Add budget tracking charts */}
        {/* TODO: Implement team collaboration tools */}
        {/* TODO: Add project templates */}
        {/* TODO: Implement milestone tracking */}
        {/* TODO: Add document management for projects */}
      </MobilePullToRefresh>
      
      {/* Quick Actions Bottom Sheet */}
      <MobileBottomSheet
        open={quickActionsOpen}
        onClose={() => setQuickActionsOpen(false)}
        title="Project Actions"
        height="auto"
        showHandle={true}
        dismissible={true}
      >
        <List sx={{ py: 0 }}>
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('Create new project');
            }}
            sx={{ 
              borderRadius: 2, 
              mb: 1,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <Add color="primary" />
            </ListItemIcon>
            <ListItemText
              primary="New Project"
              secondary="Create a new project"
            />
          </ListItem>
          
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('View project templates');
            }}
            sx={{ 
              borderRadius: 2, 
              mb: 1,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <Assignment color="secondary" />
            </ListItemIcon>
            <ListItemText
              primary="Project Templates"
              secondary="Use predefined templates"
            />
          </ListItem>
          
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('Project analytics');
            }}
            sx={{ 
              borderRadius: 2, 
              mb: 1,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <Analytics color="info" />
            </ListItemIcon>
            <ListItemText
              primary="Project Analytics"
              secondary="View performance metrics"
            />
          </ListItem>
          
          <ListItem 
            button 
            onClick={() => {
              setQuickActionsOpen(false);
              console.log('Team management');
            }}
            sx={{ 
              borderRadius: 2,
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <ListItemIcon>
              <Group color="success" />
            </ListItemIcon>
            <ListItemText
              primary="Team Management"
              secondary="Manage project teams"
            />
          </ListItem>
        </List>
      </MobileBottomSheet>

      {/* Contextual Actions */}
      <MobileContextualActions
        actions={contextualActions}
        primaryAction={{
          icon: <Add />,
          name: 'New Project',
          onClick: () => setQuickActionsOpen(true),
          color: 'primary'
        }}
      />
    </MobileDashboardLayout>
  );
};

export default MobileProjects;