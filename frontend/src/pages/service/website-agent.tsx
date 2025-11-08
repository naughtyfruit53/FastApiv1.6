// frontend/src/pages/service/website-agent.tsx

import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Typography,
  Grid,
  Chip,
  IconButton,
  Menu,
  MenuItem,
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
} from '@mui/material';
import {
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  Launch as LaunchIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  CloudUpload as DeployIcon,
  Settings as SettingsIcon,
  Public as PublicIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { format } from 'date-fns';
import DashboardLayout from '../../components/DashboardLayout';
import WebsiteAgentWizard from '../../components/WebsiteAgentWizard';
import { ProtectedPage } from '@/components/ProtectedPage';
import websiteAgentService, {
  WebsiteProject,
} from '../../services/websiteAgentService';

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
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const WebsiteAgentPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [wizardOpen, setWizardOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState<WebsiteProject | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuProject, setMenuProject] = useState<WebsiteProject | null>(null);
  const [currentTab, setCurrentTab] = useState(0);

  // Fetch projects
  const {
    data: projects = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['website-projects'],
    queryFn: () => websiteAgentService.listProjects(),
  });

  // Fetch deployments for selected project
  const { data: deployments = [] } = useQuery({
    queryKey: ['website-deployments', selectedProject?.id],
    queryFn: () => websiteAgentService.listDeployments(selectedProject!.id),
    enabled: !!selectedProject && currentTab === 1,
  });

  // Fetch maintenance logs for selected project
  const { data: maintenanceLogs = [] } = useQuery({
    queryKey: ['website-maintenance', selectedProject?.id],
    queryFn: () => websiteAgentService.listMaintenanceLogs(selectedProject!.id),
    enabled: !!selectedProject && currentTab === 2,
  });

  // Delete project mutation
  const deleteProjectMutation = useMutation({
    mutationFn: (projectId: number) => websiteAgentService.deleteProject(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['website-projects'] });
      toast.success('Project deleted successfully');
      setSelectedProject(null);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete project');
    },
  });

  // Deploy project mutation
  const deployProjectMutation = useMutation({
    mutationFn: (projectId: number) =>
      websiteAgentService.deployProject(projectId, {
        project_id: projectId,
        deployment_version: `v${Date.now()}`,
        deployment_provider: 'vercel',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['website-projects'] });
      queryClient.invalidateQueries({ queryKey: ['website-deployments'] });
      toast.success('Deployment started successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to deploy project');
    },
  });

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, project: WebsiteProject) => {
    setAnchorEl(event.currentTarget);
    setMenuProject(project);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setMenuProject(null);
  };

  const handleDelete = () => {
    if (menuProject) {
      if (window.confirm(`Are you sure you want to delete "${menuProject.project_name}"?`)) {
        deleteProjectMutation.mutate(menuProject.id);
      }
    }
    handleMenuClose();
  };

  const handleDeploy = () => {
    if (menuProject) {
      deployProjectMutation.mutate(menuProject.id);
    }
    handleMenuClose();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'deployed':
        return 'success';
      case 'in_progress':
        return 'warning';
      case 'draft':
        return 'default';
      case 'archived':
        return 'error';
      default:
        return 'default';
    }
  };

  const getDeploymentStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'failed':
        return 'error';
      case 'in_progress':
        return 'warning';
      case 'pending':
        return 'default';
      default:
        return 'default';
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <Alert severity="error">Failed to load website projects</Alert>
      </DashboardLayout>
    );
  }

  return (


    <ProtectedPage moduleKey="service" action="read">
    <DashboardLayout>
      <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            Website Agent
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setWizardOpen(true)}
          >
            Create Website
          </Button>
        </Box>

        {projects.length === 0 ? (
          <Card>
            <CardContent>
              <Box textAlign="center" py={4}>
                <PublicIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  No Website Projects Yet
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={3}>
                  Create your first website project to get started with automated website
                  customization and deployment.
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setWizardOpen(true)}
                >
                  Create First Project
                </Button>
              </Box>
            </CardContent>
          </Card>
        ) : (
          <Grid container spacing={3}>
            <Grid item xs={12} md={selectedProject ? 4 : 12}>
              <Grid container spacing={2}>
                {projects.map((project) => (
                  <Grid item xs={12} key={project.id}>
                    <Card
                      sx={{
                        cursor: 'pointer',
                        border:
                          selectedProject?.id === project.id ? '2px solid primary.main' : 'none',
                      }}
                      onClick={() => setSelectedProject(project)}
                    >
                      <CardContent>
                        <Box display="flex" justifyContent="space-between" alignItems="start">
                          <Box flex={1}>
                            <Typography variant="h6" gutterBottom>
                              {project.project_name}
                            </Typography>
                            <Box display="flex" gap={1} mb={1}>
                              <Chip
                                label={project.project_type}
                                size="small"
                                variant="outlined"
                              />
                              <Chip
                                label={project.status}
                                size="small"
                                color={getStatusColor(project.status) as any}
                              />
                            </Box>
                            {project.site_description && (
                              <Typography variant="body2" color="text.secondary" noWrap>
                                {project.site_description}
                              </Typography>
                            )}
                          </Box>
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleMenuClick(e, project);
                            }}
                          >
                            <MoreVertIcon />
                          </IconButton>
                        </Box>
                      </CardContent>
                      {project.deployment_url && (
                        <CardActions>
                          <Button
                            size="small"
                            startIcon={<LaunchIcon />}
                            href={project.deployment_url}
                            target="_blank"
                            onClick={(e) => e.stopPropagation()}
                          >
                            View Site
                          </Button>
                        </CardActions>
                      )}
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Grid>

            {selectedProject && (
              <Grid item xs={12} md={8}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Typography variant="h5">{selectedProject.project_name}</Typography>
                      <Box>
                        <Button
                          startIcon={<DeployIcon />}
                          onClick={() => deployProjectMutation.mutate(selectedProject.id)}
                          disabled={deployProjectMutation.isPending}
                        >
                          Deploy
                        </Button>
                        <IconButton>
                          <SettingsIcon />
                        </IconButton>
                      </Box>
                    </Box>

                    <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
                      <Tab label="Overview" />
                      <Tab label="Deployments" />
                      <Tab label="Maintenance" />
                    </Tabs>

                    <TabPanel value={currentTab} index={0}>
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="body2" color="text.secondary">
                            Theme
                          </Typography>
                          <Typography variant="body1">{selectedProject.theme}</Typography>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <Typography variant="body2" color="text.secondary">
                            Status
                          </Typography>
                          <Chip
                            label={selectedProject.status}
                            size="small"
                            color={getStatusColor(selectedProject.status) as any}
                          />
                        </Grid>
                        {selectedProject.domain && (
                          <Grid item xs={12}>
                            <Typography variant="body2" color="text.secondary">
                              Domain
                            </Typography>
                            <Typography variant="body1">{selectedProject.domain}</Typography>
                          </Grid>
                        )}
                        {selectedProject.site_title && (
                          <Grid item xs={12}>
                            <Typography variant="body2" color="text.secondary">
                              Site Title
                            </Typography>
                            <Typography variant="body1">{selectedProject.site_title}</Typography>
                          </Grid>
                        )}
                        {selectedProject.site_description && (
                          <Grid item xs={12}>
                            <Typography variant="body2" color="text.secondary">
                              Description
                            </Typography>
                            <Typography variant="body1">
                              {selectedProject.site_description}
                            </Typography>
                          </Grid>
                        )}
                        <Grid item xs={12} sm={6}>
                          <Typography variant="body2" color="text.secondary">
                            Chatbot Enabled
                          </Typography>
                          <Typography variant="body1">
                            {selectedProject.chatbot_enabled ? 'Yes' : 'No'}
                          </Typography>
                        </Grid>
                        {selectedProject.last_deployed_at && (
                          <Grid item xs={12} sm={6}>
                            <Typography variant="body2" color="text.secondary">
                              Last Deployed
                            </Typography>
                            <Typography variant="body1">
                              {format(
                                new Date(selectedProject.last_deployed_at),
                                'MMM dd, yyyy HH:mm'
                              )}
                            </Typography>
                          </Grid>
                        )}
                      </Grid>
                    </TabPanel>

                    <TabPanel value={currentTab} index={1}>
                      {deployments.length === 0 ? (
                        <Alert severity="info">No deployments yet</Alert>
                      ) : (
                        <TableContainer>
                          <Table>
                            <TableHead>
                              <TableRow>
                                <TableCell>Version</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell>Provider</TableCell>
                                <TableCell>Date</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {deployments.map((deployment) => (
                                <TableRow key={deployment.id}>
                                  <TableCell>{deployment.deployment_version}</TableCell>
                                  <TableCell>
                                    <Chip
                                      label={deployment.deployment_status}
                                      size="small"
                                      color={
                                        getDeploymentStatusColor(
                                          deployment.deployment_status
                                        ) as any
                                      }
                                    />
                                  </TableCell>
                                  <TableCell>{deployment.deployment_provider}</TableCell>
                                  <TableCell>
                                    {format(new Date(deployment.created_at), 'MMM dd, yyyy HH:mm')}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      )}
                    </TabPanel>

                    <TabPanel value={currentTab} index={2}>
                      {maintenanceLogs.length === 0 ? (
                        <Alert severity="info">No maintenance logs yet</Alert>
                      ) : (
                        <TableContainer>
                          <Table>
                            <TableHead>
                              <TableRow>
                                <TableCell>Title</TableCell>
                                <TableCell>Type</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell>Date</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {maintenanceLogs.map((log) => (
                                <TableRow key={log.id}>
                                  <TableCell>{log.title}</TableCell>
                                  <TableCell>{log.maintenance_type}</TableCell>
                                  <TableCell>
                                    <Chip label={log.status} size="small" />
                                  </TableCell>
                                  <TableCell>
                                    {format(new Date(log.created_at), 'MMM dd, yyyy HH:mm')}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      )}
                    </TabPanel>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        )}

        <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
          <MenuItem onClick={() => console.log('Edit')}>
            <EditIcon fontSize="small" sx={{ mr: 1 }} />
            Edit
          </MenuItem>
          <MenuItem onClick={handleDeploy}>
            <DeployIcon fontSize="small" sx={{ mr: 1 }} />
            Deploy
          </MenuItem>
          <MenuItem onClick={handleDelete}>
            <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
            Delete
          </MenuItem>
        </Menu>

        <WebsiteAgentWizard open={wizardOpen} onClose={() => setWizardOpen(false)} />
      </Box>
    </DashboardLayout>


    </ProtectedPage>


  
  );
};

export default WebsiteAgentPage;
