// frontend/src/pages/projects/resources.tsx
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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
} from "@mui/material";
import {
  Add,
  Edit,
  People,
  AttachMoney,
  Search,
  Assignment,
  ExpandMore,
  Person,
  Build,
  LocalShipping,
  AccountBalance,
} from "@mui/icons-material";

// Types
interface Resource {
  id: number;
  resource_name: string;
  resource_type: 'human' | 'equipment' | 'material' | 'budget';
  skills: string[];
  hourly_rate: number;
  availability_start: Date;
  availability_end: Date;
  total_allocation: number;
  current_utilization: number;
  projects: ResourceProject[];
  contact_info?: {
    email: string;
    phone: string;
    department: string;
  };
}

interface ResourceProject {
  project_id: number;
  project_name: string;
  allocation_percentage: number;
  start_date: Date;
  end_date: Date;
  role: string;
}

interface ResourceAllocation {
  id: number;
  resource_id: number;
  project_id: number;
  title: string;
  start: Date;
  end: Date;
  allDay: boolean;
  resource: {
    color: string;
  };
}

interface SkillMatrix {
  skill_name: string;
  required_level: number;
  available_resources: {
    resource_id: number;
    resource_name: string;
    skill_level: number;
    availability: number;
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
      id={`resources-tabpanel-${index}`}
      aria-labelledby={`resources-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ResourceManagementPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [resources, setResources] = useState<Resource[]>([]);
  const [allocations, setAllocations] = useState<ResourceAllocation[]>([]);
  const [skillMatrix, setSkillMatrix] = useState<SkillMatrix[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    loadMockData();
  }, []);

  const loadMockData = () => {
    setLoading(true);
    
    // Mock resource data
    const mockResources: Resource[] = [
      {
        id: 1,
        resource_name: "John Smith",
        resource_type: "human",
        skills: ["React", "Node.js", "Python", "Project Management"],
        hourly_rate: 85,
        availability_start: new Date("2024-01-01"),
        availability_end: new Date("2024-12-31"),
        total_allocation: 100,
        current_utilization: 85,
        contact_info: {
          email: "john.smith@company.com",
          phone: "+1-555-0123",
          department: "Engineering"
        },
        projects: [
          {
            project_id: 1,
            project_name: "ERP Implementation",
            allocation_percentage: 60,
            start_date: new Date("2024-01-15"),
            end_date: new Date("2024-06-30"),
            role: "Lead Developer"
          },
          {
            project_id: 2,
            project_name: "Mobile App",
            allocation_percentage: 25,
            start_date: new Date("2024-03-01"),
            end_date: new Date("2024-05-15"),
            role: "Senior Developer"
          }
        ]
      },
      {
        id: 2,
        resource_name: "Sarah Johnson",
        resource_type: "human",
        skills: ["UI/UX Design", "Figma", "Adobe Creative Suite", "User Research"],
        hourly_rate: 75,
        availability_start: new Date("2024-01-01"),
        availability_end: new Date("2024-12-31"),
        total_allocation: 100,
        current_utilization: 70,
        contact_info: {
          email: "sarah.johnson@company.com",
          phone: "+1-555-0124",
          department: "Design"
        },
        projects: [
          {
            project_id: 2,
            project_name: "Mobile App",
            allocation_percentage: 70,
            start_date: new Date("2024-02-01"),
            end_date: new Date("2024-05-15"),
            role: "UI/UX Designer"
          }
        ]
      },
      {
        id: 3,
        resource_name: "Development Server",
        resource_type: "equipment",
        skills: ["High Performance Computing", "Docker", "Kubernetes"],
        hourly_rate: 25,
        availability_start: new Date("2024-01-01"),
        availability_end: new Date("2024-12-31"),
        total_allocation: 100,
        current_utilization: 45,
        projects: [
          {
            project_id: 1,
            project_name: "ERP Implementation",
            allocation_percentage: 30,
            start_date: new Date("2024-02-01"),
            end_date: new Date("2024-06-30"),
            role: "Development Environment"
          },
          {
            project_id: 3,
            project_name: "Cloud Migration",
            allocation_percentage: 15,
            start_date: new Date("2024-04-01"),
            end_date: new Date("2024-07-31"),
            role: "Testing Environment"
          }
        ]
      },
      {
        id: 4,
        resource_name: "AWS Infrastructure Budget",
        resource_type: "budget",
        skills: ["Cloud Computing", "AWS", "Infrastructure"],
        hourly_rate: 0,
        availability_start: new Date("2024-01-01"),
        availability_end: new Date("2024-12-31"),
        total_allocation: 50000,
        current_utilization: 32000,
        projects: [
          {
            project_id: 1,
            project_name: "ERP Implementation",
            allocation_percentage: 40,
            start_date: new Date("2024-01-01"),
            end_date: new Date("2024-06-30"),
            role: "Infrastructure Cost"
          },
          {
            project_id: 3,
            project_name: "Cloud Migration",
            allocation_percentage: 24,
            start_date: new Date("2024-04-01"),
            end_date: new Date("2024-07-31"),
            role: "Migration Cost"
          }
        ]
      }
    ];

    // Mock allocation data for calendar
    const mockAllocations: ResourceAllocation[] = [
      {
        id: 1,
        resource_id: 1,
        project_id: 1,
        title: "John Smith - ERP Implementation",
        start: new Date("2024-01-15"),
        end: new Date("2024-06-30"),
        allDay: false,
        resource: { color: "#2196f3" }
      },
      {
        id: 2,
        resource_id: 1,
        project_id: 2,
        title: "John Smith - Mobile App",
        start: new Date("2024-03-01"),
        end: new Date("2024-05-15"),
        allDay: false,
        resource: { color: "#4caf50" }
      },
      {
        id: 3,
        resource_id: 2,
        project_id: 2,
        title: "Sarah Johnson - Mobile App",
        start: new Date("2024-02-01"),
        end: new Date("2024-05-15"),
        allDay: false,
        resource: { color: "#ff9800" }
      }
    ];

    // Mock skill matrix
    const mockSkillMatrix: SkillMatrix[] = [
      {
        skill_name: "React",
        required_level: 4,
        available_resources: [
          { resource_id: 1, resource_name: "John Smith", skill_level: 5, availability: 15 },
        ]
      },
      {
        skill_name: "UI/UX Design",
        required_level: 4,
        available_resources: [
          { resource_id: 2, resource_name: "Sarah Johnson", skill_level: 5, availability: 30 },
        ]
      },
      {
        skill_name: "Project Management",
        required_level: 3,
        available_resources: [
          { resource_id: 1, resource_name: "John Smith", skill_level: 4, availability: 15 },
        ]
      }
    ];

    setTimeout(() => {
      setResources(mockResources);
      setAllocations(mockAllocations);
      setSkillMatrix(mockSkillMatrix);
      setLoading(false);
    }, 1000);
  };

  const getResourceTypeIcon = (type: string) => {
    switch (type) {
      case 'human':
        return <Person />;
      case 'equipment':
        return <Build />;
      case 'material':
        return <LocalShipping />;
      case 'budget':
        return <AccountBalance />;
      default:
        return <Assignment />;
    }
  };

  const getResourceTypeColor = (type: string) => {
    switch (type) {
      case 'human':
        return 'primary';
      case 'equipment':
        return 'warning';
      case 'material':
        return 'success';
      case 'budget':
        return 'info';
      default:
        return 'default';
    }
  };

  const getUtilizationColor = (utilization: number, total: number) => {
    const percentage = (utilization / total) * 100;
    if (percentage >= 90) return 'error';
    if (percentage >= 70) return 'warning';
    if (percentage >= 50) return 'success';
    return 'info';
  };

  const filteredResources = resources.filter(resource => {
    const matchesSearch = resource.resource_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         resource.skills.some(skill => skill.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesType = typeFilter === 'all' || resource.resource_type === typeFilter;
    return matchesSearch && matchesType;
  });

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Resource Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setDialogOpen(true)}
        >
          Add Resource
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <People sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Resources
                  </Typography>
                  <Typography variant="h4">
                    {resources.length}
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
                <Person sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Human Resources
                  </Typography>
                  <Typography variant="h4">
                    {resources.filter(r => r.resource_type === 'human').length}
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
                <Build sx={{ fontSize: 40, color: 'warning.main', mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Equipment
                  </Typography>
                  <Typography variant="h4">
                    {resources.filter(r => r.resource_type === 'equipment').length}
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
                <AttachMoney sx={{ fontSize: 40, color: 'info.main', mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Avg Utilization
                  </Typography>
                  <Typography variant="h4">
                    {Math.round(resources.reduce((acc, r) => acc + (r.current_utilization / r.total_allocation * 100), 0) / resources.length)}%
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ width: '100%' }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Resource Pool" />
          <Tab label="Allocation Calendar" />
          <Tab label="Skill Matrix" />
          <Tab label="Utilization Analysis" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {/* Filters */}
          <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
            <TextField
              placeholder="Search resources or skills..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1 }} />,
              }}
              sx={{ minWidth: 300 }}
            />
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Resource Type</InputLabel>
              <Select
                value={typeFilter}
                label="Resource Type"
                onChange={(e) => setTypeFilter(e.target.value as string)}
              >
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="human">Human</MenuItem>
                <MenuItem value="equipment">Equipment</MenuItem>
                <MenuItem value="material">Material</MenuItem>
                <MenuItem value="budget">Budget</MenuItem>
              </Select>
            </FormControl>
          </Box>

          {/* Resource Grid */}
          <Grid container spacing={3}>
            {filteredResources.map((resource) => (
              <Grid item xs={12} md={6} lg={4} key={resource.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: `${getResourceTypeColor(resource.resource_type)}.main` }}>
                          {getResourceTypeIcon(resource.resource_type)}
                        </Avatar>
                        <Box>
                          <Typography variant="h6" gutterBottom>
                            {resource.resource_name}
                          </Typography>
                          <Chip
                            label={resource.resource_type}
                            color={getResourceTypeColor(resource.resource_type) as any}
                            size="small"
                          />
                        </Box>
                      </Box>
                      <IconButton size="small">
                        <Edit />
                      </IconButton>
                    </Box>

                    {/* Skills */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                        Skills/Capabilities
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {resource.skills.slice(0, 3).map((skill, index) => (
                          <Chip key={index} label={skill} size="small" variant="outlined" />
                        ))}
                        {resource.skills.length > 3 && (
                          <Chip label={`+${resource.skills.length - 3} more`} size="small" variant="outlined" />
                        )}
                      </Box>
                    </Box>

                    {/* Utilization */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                        Current Utilization
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={(resource.current_utilization / resource.total_allocation) * 100}
                          color={getUtilizationColor(resource.current_utilization, resource.total_allocation) as any}
                          sx={{ flex: 1, height: 8, borderRadius: 1 }}
                        />
                        <Typography variant="body2">
                          {Math.round((resource.current_utilization / resource.total_allocation) * 100)}%
                        </Typography>
                      </Box>
                    </Box>

                    {/* Rate and Contact */}
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          {resource.resource_type === 'budget' ? 'Budget' : 'Rate'}
                        </Typography>
                        <Typography variant="h6" color="primary">
                          {resource.resource_type === 'budget' 
                            ? `$${resource.total_allocation.toLocaleString()}`
                            : `$${resource.hourly_rate}/hr`
                          }
                        </Typography>
                      </Box>
                      {resource.contact_info && (
                        <Box sx={{ textAlign: 'right' }}>
                          <Typography variant="body2" color="textSecondary">
                            {resource.contact_info.department}
                          </Typography>
                          <Typography variant="body2">
                            {resource.contact_info.email}
                          </Typography>
                        </Box>
                      )}
                    </Box>

                    {/* Current Projects */}
                    {resource.projects.length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                          Current Projects ({resource.projects.length})
                        </Typography>
                        <Stack spacing={0.5}>
                          {resource.projects.slice(0, 2).map((project) => (
                            <Box key={project.project_id} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="body2" noWrap sx={{ flex: 1 }}>
                                {project.project_name}
                              </Typography>
                              <Chip
                                label={`${project.allocation_percentage}%`}
                                size="small"
                                color="info"
                              />
                            </Box>
                          ))}
                          {resource.projects.length > 2 && (
                            <Typography variant="body2" color="textSecondary">
                              +{resource.projects.length - 2} more projects
                            </Typography>
                          )}
                        </Stack>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {/* Resource Allocation Timeline */}
          <Typography variant="h6" gutterBottom>
            Resource Allocation Timeline
          </Typography>
          <Box sx={{ p: 3 }}>
            <Alert severity="info">
              Calendar view will be implemented in the next phase. 
              For now, you can view resource allocations in the Resource Pool tab.
            </Alert>
            <Typography variant="body1" sx={{ mt: 2 }}>
              This section will show:
            </Typography>
            <ul>
              <li>Visual timeline of resource allocations</li>
              <li>Conflict detection and resolution</li>
              <li>Drag-and-drop scheduling</li>
              <li>Resource availability calendar</li>
            </ul>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {/* Skill Matrix */}
          <Typography variant="h6" gutterBottom>
            Skill Matrix & Resource Matching
          </Typography>
          <Stack spacing={2}>
            {skillMatrix.map((skill, index) => (
              <Accordion key={index}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', mr: 2 }}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {skill.skill_name}
                    </Typography>
                    <Chip
                      label={`Required Level: ${skill.required_level}/5`}
                      color="primary"
                      size="small"
                    />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Resource Name</TableCell>
                          <TableCell>Skill Level</TableCell>
                          <TableCell>Availability (%)</TableCell>
                          <TableCell>Match Score</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {skill.available_resources.map((resource) => (
                          <TableRow key={resource.resource_id}>
                            <TableCell>{resource.resource_name}</TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <LinearProgress
                                  variant="determinate"
                                  value={(resource.skill_level / 5) * 100}
                                  color={resource.skill_level >= skill.required_level ? 'success' : 'warning'}
                                  sx={{ width: 80, height: 6, borderRadius: 1 }}
                                />
                                <Typography variant="body2">
                                  {resource.skill_level}/5
                                </Typography>
                              </Box>
                            </TableCell>
                            <TableCell>{resource.availability}%</TableCell>
                            <TableCell>
                              <Chip
                                label={resource.skill_level >= skill.required_level ? 'Perfect Match' : 'Partial Match'}
                                color={resource.skill_level >= skill.required_level ? 'success' : 'warning'}
                                size="small"
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </AccordionDetails>
              </Accordion>
            ))}
          </Stack>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          {/* Utilization Analysis */}
          <Typography variant="h6" gutterBottom>
            Resource Utilization Analysis
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Resource Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Total Capacity</TableCell>
                  <TableCell>Current Utilization</TableCell>
                  <TableCell>Available Capacity</TableCell>
                  <TableCell>Utilization %</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {resources.map((resource) => {
                  const utilizationPercent = (resource.current_utilization / resource.total_allocation) * 100;
                  const availableCapacity = resource.total_allocation - resource.current_utilization;
                  
                  return (
                    <TableRow key={resource.id} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Avatar sx={{ bgcolor: `${getResourceTypeColor(resource.resource_type)}.main`, width: 32, height: 32 }}>
                            {getResourceTypeIcon(resource.resource_type)}
                          </Avatar>
                          {resource.resource_name}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={resource.resource_type}
                          color={getResourceTypeColor(resource.resource_type) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {resource.resource_type === 'budget' 
                          ? `$${resource.total_allocation.toLocaleString()}`
                          : `${resource.total_allocation}${resource.resource_type === 'human' ? ' hrs' : ' units'}`
                        }
                      </TableCell>
                      <TableCell>
                        {resource.resource_type === 'budget' 
                          ? `$${resource.current_utilization.toLocaleString()}`
                          : `${resource.current_utilization}${resource.resource_type === 'human' ? ' hrs' : ' units'}`
                        }
                      </TableCell>
                      <TableCell>
                        {resource.resource_type === 'budget' 
                          ? `$${availableCapacity.toLocaleString()}`
                          : `${availableCapacity}${resource.resource_type === 'human' ? ' hrs' : ' units'}`
                        }
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={utilizationPercent}
                            color={getUtilizationColor(resource.current_utilization, resource.total_allocation) as any}
                            sx={{ width: 80, height: 8, borderRadius: 1 }}
                          />
                          <Typography variant="body2">
                            {Math.round(utilizationPercent)}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={
                            utilizationPercent >= 90 ? 'Overallocated' :
                            utilizationPercent >= 70 ? 'Well Utilized' :
                            utilizationPercent >= 50 ? 'Available' : 'Underutilized'
                          }
                          color={getUtilizationColor(resource.current_utilization, resource.total_allocation) as any}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>
      </Paper>

      {/* Add Resource Dialog Placeholder */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add New Resource</DialogTitle>
        <DialogContent>
          <Typography>Resource creation form will be implemented in the next phase.</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained">Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ResourceManagementPage;