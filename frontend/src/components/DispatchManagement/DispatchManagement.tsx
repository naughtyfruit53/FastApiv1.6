'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
  Alert,
  CircularProgress,
  Tab,
  Tabs,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Pagination
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  LocalShipping as DispatchIcon,
  Build as InstallationIcon,
  Visibility as ViewIcon,
  FilterList as FilterIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';
import { dispatchService, DispatchOrderInDB, InstallationJobInDB } from '../../services/dispatchService';
import {
  DISPATCH_ORDER_STATUS_CONFIG,
  INSTALLATION_JOB_STATUS_CONFIG,
  INSTALLATION_JOB_PRIORITY_CONFIG,
  hasDispatchManagementPermission,
  hasDispatchViewPermission,
  hasInstallationManagementPermission,
  hasInstallationViewPermission
} from '../../types/dispatch.types';
import DispatchOrderDialog from './DispatchOrderDialog';
import InstallationJobDialog from './InstallationJobDialog';
import InstallationSchedulePromptModal from './InstallationSchedulePromptModal';

interface DispatchManagementProps {
  organizationId: number;
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
      id={`dispatch-tabpanel-${index}`}
      aria-labelledby={`dispatch-tab-${index}`}
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

const DispatchManagement: React.FC<DispatchManagementProps> = ({ organizationId }) => {
  const { user } = useAuth();
  const [currentTab, setCurrentTab] = useState(0);
  const [dispatchOrders, setDispatchOrders] = useState<DispatchOrderInDB[]>([]);
  const [installationJobs, setInstallationJobs] = useState<InstallationJobInDB[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Pagination
  const [dispatchPage, setDispatchPage] = useState(1);
  const [installationPage, setInstallationPage] = useState(1);
  const [itemsPerPage] = useState(10);
  
  // Filters
  const [dispatchStatusFilter, setDispatchStatusFilter] = useState('');
  const [installationStatusFilter, setInstallationStatusFilter] = useState('');
  const [installationPriorityFilter, setInstallationPriorityFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Dialog states
  const [dispatchOrderDialogOpen, setDispatchOrderDialogOpen] = useState(false);
  const [installationJobDialogOpen, setInstallationJobDialogOpen] = useState(false);
  const [installationPromptOpen, setInstallationPromptOpen] = useState(false);
  const [selectedDispatchOrder, setSelectedDispatchOrder] = useState<DispatchOrderInDB | null>(null);
  const [selectedInstallationJob, setSelectedInstallationJob] = useState<InstallationJobInDB | null>(null);
  const [editMode, setEditMode] = useState(false);

  // Check permissions
  const canManageDispatch = user?.role ? hasDispatchManagementPermission(user.role) : false;
  const canViewDispatch = user?.role ? hasDispatchViewPermission(user.role) : false;
  const canManageInstallation = user?.role ? hasInstallationManagementPermission(user.role) : false;
  const canViewInstallation = user?.role ? hasInstallationViewPermission(user.role) : false;

  // Load data
  useEffect(() => {
    loadData();
  }, [dispatchPage, installationPage, dispatchStatusFilter, installationStatusFilter, installationPriorityFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [dispatchResponse, installationResponse] = await Promise.all([
        canViewDispatch ? dispatchService.getDispatchOrders({
          skip: (dispatchPage - 1) * itemsPerPage,
          limit: itemsPerPage,
          filter: dispatchStatusFilter ? { status: dispatchStatusFilter as any } : undefined
        }) : Promise.resolve([]),
        canViewInstallation ? dispatchService.getInstallationJobs({
          skip: (installationPage - 1) * itemsPerPage,
          limit: itemsPerPage,
          filter: {
            ...(installationStatusFilter ? { status: installationStatusFilter as any } : {}),
            ...(installationPriorityFilter ? { priority: installationPriorityFilter as any } : {})
          }
        }) : Promise.resolve([])
      ]);

      setDispatchOrders(dispatchResponse);
      setInstallationJobs(installationResponse);
    } catch (err: any) {
      console.error('Error loading dispatch data:', err);
      setError(err.message || 'Failed to load dispatch data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDispatchOrder = () => {
    setSelectedDispatchOrder(null);
    setEditMode(false);
    setDispatchOrderDialogOpen(true);
  };

  const handleEditDispatchOrder = (order: DispatchOrderInDB) => {
    setSelectedDispatchOrder(order);
    setEditMode(true);
    setDispatchOrderDialogOpen(true);
  };

  const handleDeleteDispatchOrder = async (orderId: number) => {
    if (!window.confirm('Are you sure you want to delete this dispatch order?')) {
      return;
    }

    try {
      await dispatchService.deleteDispatchOrder(orderId);
      await loadData();
    } catch (err: any) {
      setError(err.message || 'Failed to delete dispatch order');
    }
  };

  const handleCreateInstallationJob = () => {
    setSelectedInstallationJob(null);
    setEditMode(false);
    setInstallationJobDialogOpen(true);
  };

  const handleEditInstallationJob = (job: InstallationJobInDB) => {
    setSelectedInstallationJob(job);
    setEditMode(true);
    setInstallationJobDialogOpen(true);
  };

  const handleDeleteInstallationJob = async (jobId: number) => {
    if (!window.confirm('Are you sure you want to delete this installation job?')) {
      return;
    }

    try {
      await dispatchService.deleteInstallationJob(jobId);
      await loadData();
    } catch (err: any) {
      setError(err.message || 'Failed to delete installation job');
    }
  };

  const renderDispatchOrderRow = (order: DispatchOrderInDB) => {
    const statusConfig = DISPATCH_ORDER_STATUS_CONFIG[order.status];
    
    return (
      <TableRow key={order.id}>
        <TableCell>{order.order_number}</TableCell>
        <TableCell>{order.customer_id}</TableCell>
        <TableCell>
          <Chip 
            label={statusConfig.label}
            color={statusConfig.color as any}
            size="small"
          />
        </TableCell>
        <TableCell>{new Date(order.created_at).toLocaleDateString()}</TableCell>
        <TableCell>
          {order.expected_delivery_date ? 
            new Date(order.expected_delivery_date).toLocaleDateString() : 
            '-'
          }
        </TableCell>
        <TableCell>{order.items.length}</TableCell>
        <TableCell>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="View">
              <IconButton 
                size="small" 
                onClick={() => handleEditDispatchOrder(order)}
              >
                <ViewIcon />
              </IconButton>
            </Tooltip>
            {canManageDispatch && (
              <>
                <Tooltip title="Edit">
                  <IconButton 
                    size="small" 
                    onClick={() => handleEditDispatchOrder(order)}
                  >
                    <EditIcon />
                  </IconButton>
                </Tooltip>
                {order.status === 'pending' && (
                  <Tooltip title="Delete">
                    <IconButton 
                      size="small" 
                      color="error"
                      onClick={() => handleDeleteDispatchOrder(order.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                )}
              </>
            )}
          </Box>
        </TableCell>
      </TableRow>
    );
  };

  const renderInstallationJobRow = (job: InstallationJobInDB) => {
    const statusConfig = INSTALLATION_JOB_STATUS_CONFIG[job.status];
    const priorityConfig = INSTALLATION_JOB_PRIORITY_CONFIG[job.priority];
    
    return (
      <TableRow key={job.id}>
        <TableCell>{job.job_number}</TableCell>
        <TableCell>{job.customer_id}</TableCell>
        <TableCell>
          <Chip 
            label={statusConfig.label}
            color={statusConfig.color as any}
            size="small"
          />
        </TableCell>
        <TableCell>
          <Chip 
            label={priorityConfig.label}
            color={priorityConfig.color as any}
            size="small"
            variant="outlined"
          />
        </TableCell>
        <TableCell>
          {job.scheduled_date ? 
            new Date(job.scheduled_date).toLocaleDateString() : 
            '-'
          }
        </TableCell>
        <TableCell>{job.assigned_technician_id || '-'}</TableCell>
        <TableCell>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="View">
              <IconButton 
                size="small" 
                onClick={() => handleEditInstallationJob(job)}
              >
                <ViewIcon />
              </IconButton>
            </Tooltip>
            {canManageInstallation && (
              <>
                <Tooltip title="Edit">
                  <IconButton 
                    size="small" 
                    onClick={() => handleEditInstallationJob(job)}
                  >
                    <EditIcon />
                  </IconButton>
                </Tooltip>
                {job.status === 'scheduled' && (
                  <Tooltip title="Delete">
                    <IconButton 
                      size="small" 
                      color="error"
                      onClick={() => handleDeleteInstallationJob(job.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                )}
              </>
            )}
          </Box>
        </TableCell>
      </TableRow>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" gutterBottom>
          Material Dispatch Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          {canManageDispatch && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleCreateDispatchOrder}
            >
              Create Dispatch Order
            </Button>
          )}
          {canManageInstallation && (
            <Button
              variant="contained"
              startIcon={<InstallationIcon />}
              onClick={handleCreateInstallationJob}
              color="secondary"
            >
              Create Installation Job
            </Button>
          )}
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={(_, newValue) => setCurrentTab(newValue)}>
          <Tab label="Dispatch Orders" />
          <Tab label="Installation Jobs" />
        </Tabs>
      </Box>

      <TabPanel value={currentTab} index={0}>
        {/* Dispatch Orders Tab */}
        <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Status Filter</InputLabel>
            <Select
              value={dispatchStatusFilter}
              onChange={(e) => setDispatchStatusFilter(e.target.value)}
              label="Status Filter"
            >
              <MenuItem value="">All Statuses</MenuItem>
              {Object.entries(DISPATCH_ORDER_STATUS_CONFIG).map(([key, config]) => (
                <MenuItem key={key} value={key}>
                  {config.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <TextField
            size="small"
            placeholder="Search orders..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />
            }}
          />
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Order Number</TableCell>
                <TableCell>Customer</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created Date</TableCell>
                <TableCell>Expected Delivery</TableCell>
                <TableCell>Items Count</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {dispatchOrders.map(renderDispatchOrderRow)}
            </TableBody>
          </Table>
        </TableContainer>

        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination
            count={Math.ceil(dispatchOrders.length / itemsPerPage)}
            page={dispatchPage}
            onChange={(_, page) => setDispatchPage(page)}
          />
        </Box>
      </TabPanel>

      <TabPanel value={currentTab} index={1}>
        {/* Installation Jobs Tab */}
        <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Status Filter</InputLabel>
            <Select
              value={installationStatusFilter}
              onChange={(e) => setInstallationStatusFilter(e.target.value)}
              label="Status Filter"
            >
              <MenuItem value="">All Statuses</MenuItem>
              {Object.entries(INSTALLATION_JOB_STATUS_CONFIG).map(([key, config]) => (
                <MenuItem key={key} value={key}>
                  {config.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Priority Filter</InputLabel>
            <Select
              value={installationPriorityFilter}
              onChange={(e) => setInstallationPriorityFilter(e.target.value)}
              label="Priority Filter"
            >
              <MenuItem value="">All Priorities</MenuItem>
              {Object.entries(INSTALLATION_JOB_PRIORITY_CONFIG).map(([key, config]) => (
                <MenuItem key={key} value={key}>
                  {config.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <TextField
            size="small"
            placeholder="Search jobs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />
            }}
          />
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Job Number</TableCell>
                <TableCell>Customer</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Priority</TableCell>
                <TableCell>Scheduled Date</TableCell>
                <TableCell>Technician</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {installationJobs.map(renderInstallationJobRow)}
            </TableBody>
          </Table>
        </TableContainer>

        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination
            count={Math.ceil(installationJobs.length / itemsPerPage)}
            page={installationPage}
            onChange={(_, page) => setInstallationPage(page)}
          />
        </Box>
      </TabPanel>

      {/* Note: Dialog components would be implemented separately */}
      {/* For now, showing placeholder text to indicate missing dialogs */}
      {dispatchOrderDialogOpen && (
        <Dialog open={dispatchOrderDialogOpen} maxWidth="lg" fullWidth>
          <DialogTitle>Dispatch Order {editMode ? 'Edit' : 'Create'}</DialogTitle>
          <DialogContent>
            <Typography>Dispatch Order Dialog component would be implemented here</Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDispatchOrderDialogOpen(false)}>Cancel</Button>
            <Button variant="contained">Save</Button>
          </DialogActions>
        </Dialog>
      )}

      {installationJobDialogOpen && (
        <Dialog open={installationJobDialogOpen} maxWidth="lg" fullWidth>
          <DialogTitle>Installation Job {editMode ? 'Edit' : 'Create'}</DialogTitle>
          <DialogContent>
            <Typography>Installation Job Dialog component would be implemented here</Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setInstallationJobDialogOpen(false)}>Cancel</Button>
            <Button variant="contained">Save</Button>
          </DialogActions>
        </Dialog>
      )}

      {installationPromptOpen && (
        <Dialog open={installationPromptOpen} maxWidth="md" fullWidth>
          <DialogTitle>Create Installation Schedule</DialogTitle>
          <DialogContent>
            <Typography>Installation Schedule Prompt Modal component would be implemented here</Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setInstallationPromptOpen(false)}>Cancel</Button>
            <Button variant="contained">Create</Button>
          </DialogActions>
        </Dialog>
      )}
    </Box>
  );
};

export default DispatchManagement;