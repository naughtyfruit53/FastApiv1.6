// frontend/src/pages/projects/planning.tsx
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
  Button,
  Stack,
  Chip,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from "@mui/material";
import {
  Add,
  Edit,
  Save,
  Cancel,
  Schedule,
  ExpandMore,
  Flag,
  CheckCircle,
  RadioButtonUnchecked,
} from "@mui/icons-material";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import { useRouter } from "next/navigation";
import { ProtectedPage } from "../../components/ProtectedPage";

// Types
interface ProjectPlan {
  id: number;
  project_name: string;
  project_code: string;
  description: string;
  start_date: Date;
  end_date: Date;
  budget: number;
  project_manager: string;
  status: string;
  milestones: Milestone[];
  tasks: Task[];
  resources: Resource[];
}

interface Milestone {
  id: number;
  milestone_name: string;
  description: string;
  due_date: Date;
  status: 'not_started' | 'in_progress' | 'completed' | 'delayed';
  completion_percentage: number;
  dependencies: number[];
}

interface Task {
  id: number;
  task_name: string;
  description: string;
  start_date: Date;
  end_date: Date;
  status: string;
  assigned_to: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  estimated_hours: number;
  actual_hours: number;
  milestone_id: number;
  dependencies: number[];
}

interface Resource {
  id: number;
  resource_name: string;
  resource_type: 'human' | 'equipment' | 'material' | 'budget';
  allocation_percentage: number;
  hourly_rate: number;
  total_cost: number;
  availability_start: Date;
  availability_end: Date;
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
      id={`planning-tabpanel-${index}`}
      aria-labelledby={`planning-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ProjectPlanningPage: React.FC = () => {
  const router = useRouter();
  const [tabValue, setTabValue] = useState(0);
  const [project, setProject] = useState<ProjectPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);

  useEffect(() => {
    // For demo purposes, load mock data
    loadMockProject();
  }, []);

  const loadMockProject = () => {
    setLoading(true);
    
    // Mock project data
    const mockProject: ProjectPlan = {
      id: 1,
      project_name: "ERP System Implementation",
      project_code: "ERP-2024-001",
      description: "Implementation of comprehensive ERP system for business operations",
      start_date: new Date("2024-01-15"),
      end_date: new Date("2024-06-30"),
      budget: 150000,
      project_manager: "John Doe",
      status: "planning",
      milestones: [
        {
          id: 1,
          milestone_name: "Requirements Analysis",
          description: "Complete business requirements analysis and documentation",
          due_date: new Date("2024-02-15"),
          status: "completed",
          completion_percentage: 100,
          dependencies: []
        },
        {
          id: 2,
          milestone_name: "System Design",
          description: "Design system architecture and database schema",
          due_date: new Date("2024-03-15"),
          status: "in_progress",
          completion_percentage: 65,
          dependencies: [1]
        },
        {
          id: 3,
          milestone_name: "Development Phase",
          description: "Core system development and module implementation",
          due_date: new Date("2024-05-15"),
          status: "not_started",
          completion_percentage: 0,
          dependencies: [2]
        },
        {
          id: 4,
          milestone_name: "Testing & Deployment",
          description: "System testing, user acceptance testing, and deployment",
          due_date: new Date("2024-06-30"),
          status: "not_started",
          completion_percentage: 0,
          dependencies: [3]
        }
      ],
      tasks: [
        {
          id: 1,
          task_name: "Stakeholder Interviews",
          description: "Conduct interviews with key stakeholders",
          start_date: new Date("2024-01-15"),
          end_date: new Date("2024-01-30"),
          status: "completed",
          assigned_to: "Alice Smith",
          priority: "high",
          estimated_hours: 40,
          actual_hours: 35,
          milestone_id: 1,
          dependencies: []
        },
        {
          id: 2,
          task_name: "Database Design",
          description: "Design normalized database schema",
          start_date: new Date("2024-02-16"),
          end_date: new Date("2024-03-01"),
          status: "in_progress",
          assigned_to: "Bob Johnson",
          priority: "high",
          estimated_hours: 60,
          actual_hours: 25,
          milestone_id: 2,
          dependencies: [1]
        }
      ],
      resources: [
        {
          id: 1,
          resource_name: "Senior Developer",
          resource_type: "human",
          allocation_percentage: 100,
          hourly_rate: 85,
          total_cost: 68000,
          availability_start: new Date("2024-01-15"),
          availability_end: new Date("2024-06-30")
        },
        {
          id: 2,
          resource_name: "Business Analyst",
          resource_type: "human",
          allocation_percentage: 50,
          hourly_rate: 65,
          total_cost: 26000,
          availability_start: new Date("2024-01-15"),
          availability_end: new Date("2024-06-30")
        }
      ]
    };

    setTimeout(() => {
      setProject(mockProject);
      setLoading(false);
    }, 1000);
  };

  const getMilestoneStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'warning';
      case 'delayed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getMilestoneIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'in_progress':
        return <Schedule color="warning" />;
      case 'delayed':
        return <Flag color="error" />;
      default:
        return <RadioButtonUnchecked color="disabled" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!project) {
    return (
      <Alert severity="error">
        Project not found
      </Alert>
    );
  }

  return (
    <ProtectedPage moduleKey="projects" action="read">
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Project Planning
          </Typography>
          <Stack direction="row" spacing={2}>
            <Button
              variant={editMode ? "outlined" : "contained"}
              startIcon={editMode ? <Cancel /> : <Edit />}
              onClick={() => setEditMode(!editMode)}
            >
              {editMode ? "Cancel" : "Edit"}
            </Button>
            {editMode && (
              <Button
                variant="contained"
                startIcon={<Save />}
                color="primary"
              >
                Save Changes
              </Button>
            )}
          </Stack>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Project Overview */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <Typography variant="h5" gutterBottom>
                  {project.project_name}
                </Typography>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  {project.project_code}
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {project.description}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="subtitle2" color="textSecondary">
                      Project Manager
                    </Typography>
                    <Typography variant="body1">{project.project_manager}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2" color="textSecondary">
                      Budget
                    </Typography>
                    <Typography variant="h6" color="primary">
                      ${project.budget.toLocaleString()}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2" color="textSecondary">
                      Duration
                    </Typography>
                    <Typography variant="body1">
                      {project.start_date.toLocaleDateString()} - {project.end_date.toLocaleDateString()}
                    </Typography>
                  </Box>
                </Stack>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Paper sx={{ width: '100%' }}>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
            <Tab label="Milestones" />
            <Tab label="Tasks" />
            <Tab label="Resources" />
            <Tab label="Timeline" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            {/* Milestones */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">Project Milestones</Typography>
              <Button startIcon={<Add />} variant="outlined">
                Add Milestone
              </Button>
            </Box>

            <Grid container spacing={3}>
              {project.milestones.map((milestone) => (
                <Grid item xs={12} md={6} key={milestone.id}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="h6" gutterBottom>
                            {milestone.milestone_name}
                          </Typography>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            {milestone.description}
                          </Typography>
                          <Chip
                            icon={getMilestoneIcon(milestone.status)}
                            label={milestone.status.replace('_', ' ')}
                            color={getMilestoneStatusColor(milestone.status) as any}
                            size="small"
                          />
                        </Box>
                        <IconButton size="small">
                          <Edit />
                        </IconButton>
                      </Box>
                      
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                          Progress: {milestone.completion_percentage}%
                        </Typography>
                        <Box sx={{ width: '100%', bgcolor: 'grey.200', borderRadius: 1 }}>
                          <Box
                            sx={{
                              width: `${milestone.completion_percentage}%`,
                              height: 8,
                              bgcolor: milestone.completion_percentage >= 80 ? 'success.main' : 
                                      milestone.completion_percentage >= 50 ? 'warning.main' : 'info.main',
                              borderRadius: 1,
                            }}
                          />
                        </Box>
                      </Box>

                      <Typography variant="body2" color="textSecondary">
                        Due: {milestone.due_date.toLocaleDateString()}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            {/* Tasks */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">Project Tasks</Typography>
              <Button startIcon={<Add />} variant="outlined">
                Add Task
              </Button>
            </Box>

            <Stack spacing={2}>
              {project.tasks.map((task) => (
                <Accordion key={task.id}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', mr: 2 }}>
                      <Box>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {task.task_name}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Assigned to: {task.assigned_to}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        <Chip
                          label={task.priority}
                          color={getPriorityColor(task.priority) as any}
                          size="small"
                        />
                        <Chip
                          label={task.status}
                          color={task.status === 'completed' ? 'success' : 'warning'}
                          size="small"
                        />
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={8}>
                        <Typography variant="body1" gutterBottom>
                          {task.description}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Duration: {task.start_date.toLocaleDateString()} - {task.end_date.toLocaleDateString()}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Stack spacing={1}>
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              Estimated Hours: {task.estimated_hours}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              Actual Hours: {task.actual_hours}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              Milestone: {project.milestones.find(m => m.id === task.milestone_id)?.milestone_name}
                            </Typography>
                          </Box>
                        </Stack>
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Stack>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            {/* Resources */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">Resource Allocation</Typography>
              <Button startIcon={<Add />} variant="outlined">
                Add Resource
              </Button>
            </Box>

            <Grid container spacing={3}>
              {project.resources.map((resource) => (
                <Grid item xs={12} md={6} key={resource.id}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Box>
                          <Typography variant="h6" gutterBottom>
                            {resource.resource_name}
                          </Typography>
                          <Chip
                            label={resource.resource_type}
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                        <IconButton size="small">
                          <Edit />
                        </IconButton>
                      </Box>
                      
                      <Stack spacing={1}>
                        <Box>
                          <Typography variant="body2" color="textSecondary">
                            Allocation: {resource.allocation_percentage}%
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="textSecondary">
                            Hourly Rate: ${resource.hourly_rate}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="primary" fontWeight="bold">
                            Total Cost: ${resource.total_cost.toLocaleString()}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="textSecondary">
                            Available: {resource.availability_start.toLocaleDateString()} - {resource.availability_end.toLocaleDateString()}
                          </Typography>
                        </Box>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            {/* Timeline */}
            <Typography variant="h6" gutterBottom>
              Project Timeline
            </Typography>
            
            <Timeline>
              {project.milestones.map((milestone, index) => (
                <TimelineItem key={milestone.id}>
                  <TimelineSeparator>
                    <TimelineDot color={getMilestoneStatusColor(milestone.status) as any}>
                      {getMilestoneIcon(milestone.status)}
                    </TimelineDot>
                    {index < project.milestones.length - 1 && <TimelineConnector />}
                  </TimelineSeparator>
                  <TimelineContent>
                    <Typography variant="h6" component="span">
                      {milestone.milestone_name}
                    </Typography>
                    <Typography color="textSecondary">
                      {milestone.description}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Due: {milestone.due_date.toLocaleDateString()}
                    </Typography>
                  </TimelineContent>
                </TimelineItem>
              ))}
            </Timeline>
          </TabPanel>
        </Paper>
      </Box>
    </LocalizationProvider>
    </ProtectedPage>
  );
};

export default ProjectPlanningPage;