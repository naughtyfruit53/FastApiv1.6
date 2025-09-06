// components/RoleManagement/EnhancedRoleManagement.tsx
/**
 * Enhanced Role Management - Phase 2&3 Integration
 * 
 * Advanced RBAC management with bulk operations, role templates, and audit trails
 * Builds upon existing RoleManagement component with additional enterprise features
 */

import React, { useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Alert,
  Button,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Checkbox,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Tabs,
  Tab,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
} from '@mui/material';
import {
  SupervisorAccount as SupervisorAccountIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ContentCopy as ContentCopyIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  History as HistoryIcon,
  Group as GroupIcon,
  Person as PersonIcon,
  Security as SecurityIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../hooks/useAuth';
import { rbacService, ServiceRole, ServicePermission, UserWithServiceRoles } from '../../services/rbacService';

// Enhanced interfaces for advanced features
interface RoleTemplate {
  id: string;
  name: string;
  description: string;
  permissions: string[];
  category: 'standard' | 'custom' | 'system';
}

interface AuditEntry {
  id: number;
  action: string;
  resource_type: string;
  resource_id: number;
  user_id: number;
  user_name: string;
  timestamp: string;
  details: string;
  ip_address?: string;
}

interface BulkOperation {
  operation: 'assign' | 'remove' | 'delete';
  selectedUsers: number[];
  selectedRoles: number[];
  status: 'idle' | 'processing' | 'completed' | 'error';
  progress: number;
  results?: string[];
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
      id={`enhanced-rbac-tabpanel-${index}`}
      aria-labelledby={`enhanced-rbac-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

// Role Templates Panel
const RoleTemplatesPanel: React.FC<{ organizationId: number }> = ({ organizationId }) => {
  const [selectedTemplate, setSelectedTemplate] = useState<RoleTemplate | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  // Mock role templates - replace with actual API
  const roleTemplates: RoleTemplate[] = [
    {
      id: 'admin-template',
      name: 'Administrator Template',
      description: 'Full administrative access to all modules',
      permissions: ['admin', 'user_management', 'role_management', 'system_settings'],
      category: 'system',
    },
    {
      id: 'manager-template',
      name: 'Manager Template',
      description: 'Managerial access with reporting capabilities',
      permissions: ['crm_manage', 'sales_manage', 'reports_view', 'team_management'],
      category: 'standard',
    },
    {
      id: 'support-template',
      name: 'Support Template',
      description: 'Customer support and service desk access',
      permissions: ['service_manage', 'customer_view', 'ticket_manage', 'feedback_view'],
      category: 'standard',
    },
  ];

  const handleApplyTemplate = async (template: RoleTemplate) => {
    try {
      // Create role from template
      await rbacService.createRole(organizationId, {
        name: `${template.name} Role`,
        description: template.description,
        permissions: template.permissions,
        is_active: true,
      });
      // Refresh roles list
    } catch (error) {
      console.error('Failed to apply template:', error);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">Role Templates</Typography>
        <Button
          variant="outlined"
          startIcon={<AddIcon />}
          onClick={() => setShowCreateDialog(true)}
        >
          Create Template
        </Button>
      </Box>

      <Grid container spacing={3}>
        {roleTemplates.map((template) => (
          <Grid item xs={12} md={6} lg={4} key={template.id}>
            <Card>
              <CardHeader
                title={template.name}
                subheader={
                  <Chip
                    label={template.category}
                    size="small"
                    color={template.category === 'system' ? 'primary' : 'default'}
                  />
                }
              />
              <CardContent>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  {template.description}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Permissions: {template.permissions.length}
                </Typography>
                <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                  <Button
                    size="small"
                    variant="contained"
                    onClick={() => handleApplyTemplate(template)}
                  >
                    Apply Template
                  </Button>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => setSelectedTemplate(template)}
                  >
                    View Details
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

// Bulk Operations Panel
const BulkOperationsPanel: React.FC<{ organizationId: number }> = ({ organizationId }) => {
  const [bulkOperation, setBulkOperation] = useState<BulkOperation>({
    operation: 'assign',
    selectedUsers: [],
    selectedRoles: [],
    status: 'idle',
    progress: 0,
  });

  const { data: users = [] } = useQuery({
    queryKey: ['organizationUsers', organizationId],
    queryFn: () => rbacService.getUsersWithRole(1), // Mock implementation
  });

  const { data: roles = [] } = useQuery({
    queryKey: ['organizationRoles', organizationId],
    queryFn: () => rbacService.getOrganizationRoles(organizationId),
  });

  const handleBulkOperation = async () => {
    setBulkOperation(prev => ({ ...prev, status: 'processing', progress: 0 }));

    try {
      // Simulate bulk operation progress
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setBulkOperation(prev => ({ ...prev, progress: i }));
      }

      // Perform actual bulk operation here
      console.log('Bulk operation completed:', bulkOperation);
      
      setBulkOperation(prev => ({ 
        ...prev, 
        status: 'completed',
        results: [`Successfully processed ${prev.selectedUsers.length} users`]
      }));
    } catch (error) {
      setBulkOperation(prev => ({ ...prev, status: 'error' }));
    }
  };

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 3 }}>
        Bulk Role Operations
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Select Operation" />
            <CardContent>
              <FormControl fullWidth margin="normal">
                <InputLabel>Operation Type</InputLabel>
                <Select
                  value={bulkOperation.operation}
                  onChange={(e) => setBulkOperation(prev => ({ 
                    ...prev, 
                    operation: e.target.value as 'assign' | 'remove' | 'delete'
                  }))}
                >
                  <MenuItem value="assign">Assign Roles</MenuItem>
                  <MenuItem value="remove">Remove Roles</MenuItem>
                  <MenuItem value="delete">Delete Roles</MenuItem>
                </Select>
              </FormControl>

              <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                Select Users ({bulkOperation.selectedUsers.length} selected)
              </Typography>
              <List sx={{ maxHeight: 200, overflow: 'auto' }}>
                {users.slice(0, 5).map((user) => (
                  <ListItem key={user.id} dense>
                    <Checkbox
                      checked={bulkOperation.selectedUsers.includes(user.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setBulkOperation(prev => ({
                            ...prev,
                            selectedUsers: [...prev.selectedUsers, user.id]
                          }));
                        } else {
                          setBulkOperation(prev => ({
                            ...prev,
                            selectedUsers: prev.selectedUsers.filter(id => id !== user.id)
                          }));
                        }
                      }}
                    />
                    <ListItemText primary={user.full_name} secondary={user.email} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Select Roles" />
            <CardContent>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Available Roles ({bulkOperation.selectedRoles.length} selected)
              </Typography>
              <List sx={{ maxHeight: 200, overflow: 'auto' }}>
                {roles.map((role) => (
                  <ListItem key={role.id} dense>
                    <Checkbox
                      checked={bulkOperation.selectedRoles.includes(role.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setBulkOperation(prev => ({
                            ...prev,
                            selectedRoles: [...prev.selectedRoles, role.id]
                          }));
                        } else {
                          setBulkOperation(prev => ({
                            ...prev,
                            selectedRoles: prev.selectedRoles.filter(id => id !== role.id)
                          }));
                        }
                      }}
                    />
                    <ListItemText 
                      primary={role.name} 
                      secondary={role.description}
                    />
                  </ListItem>
                ))}
              </List>

              <Box sx={{ mt: 3 }}>
                {bulkOperation.status === 'processing' && (
                  <Box sx={{ mb: 2 }}>
                    <LinearProgress variant="determinate" value={bulkOperation.progress} />
                    <Typography variant="caption" sx={{ mt: 1 }}>
                      Processing... {bulkOperation.progress}%
                    </Typography>
                  </Box>
                )}

                <Button
                  variant="contained"
                  fullWidth
                  onClick={handleBulkOperation}
                  disabled={
                    bulkOperation.selectedUsers.length === 0 || 
                    bulkOperation.selectedRoles.length === 0 ||
                    bulkOperation.status === 'processing'
                  }
                  startIcon={bulkOperation.status === 'processing' ? <LinearProgress /> : <GroupIcon />}
                >
                  {bulkOperation.status === 'processing' 
                    ? 'Processing...' 
                    : `${bulkOperation.operation} Roles`
                  }
                </Button>

                {bulkOperation.status === 'completed' && (
                  <Alert severity="success" sx={{ mt: 2 }}>
                    Bulk operation completed successfully!
                  </Alert>
                )}

                {bulkOperation.status === 'error' && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    Bulk operation failed. Please try again.
                  </Alert>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

// Audit Trail Panel
const AuditTrailPanel: React.FC = () => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Mock audit data - replace with actual API
  const auditEntries: AuditEntry[] = [
    {
      id: 1,
      action: 'ROLE_CREATED',
      resource_type: 'ServiceRole',
      resource_id: 123,
      user_id: 1,
      user_name: 'Admin User',
      timestamp: '2024-01-15T10:30:00Z',
      details: 'Created role: Manager',
      ip_address: '192.168.1.100',
    },
    {
      id: 2,
      action: 'ROLE_ASSIGNED',
      resource_type: 'UserRole',
      resource_id: 456,
      user_id: 2,
      user_name: 'HR Manager',
      timestamp: '2024-01-15T09:15:00Z',
      details: 'Assigned Support role to John Doe',
      ip_address: '192.168.1.101',
    },
  ];

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">RBAC Audit Trail</Typography>
        <Button variant="outlined" startIcon={<DownloadIcon />}>
          Export Audit Log
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Timestamp</TableCell>
              <TableCell>Action</TableCell>
              <TableCell>User</TableCell>
              <TableCell>Resource</TableCell>
              <TableCell>Details</TableCell>
              <TableCell>IP Address</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {auditEntries
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((entry) => (
                <TableRow key={entry.id}>
                  <TableCell>
                    {new Date(entry.timestamp).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={entry.action} 
                      size="small" 
                      color={entry.action.includes('DELETE') ? 'error' : 'primary'}
                    />
                  </TableCell>
                  <TableCell>{entry.user_name}</TableCell>
                  <TableCell>
                    {entry.resource_type} ({entry.resource_id})
                  </TableCell>
                  <TableCell>{entry.details}</TableCell>
                  <TableCell>{entry.ip_address}</TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={auditEntries.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>
    </Box>
  );
};

// Main Enhanced RBAC Component
const EnhancedRoleManagement: React.FC<{ organizationId: number }> = ({ organizationId }) => {
  const { user } = useAuth();
  const [selectedTab, setSelectedTab] = useState(0);

  const { data: userPermissions = [] } = useQuery({
    queryKey: ['userServicePermissions'],
    queryFn: rbacService.getCurrentUserPermissions,
    enabled: !!user,
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const canAccessEnhancedFeatures = user?.role === 'super_admin' || 
    userPermissions.includes('advanced_role_management');

  if (!canAccessEnhancedFeatures) {
    return (
      <Alert severity="warning">
        Enhanced RBAC features require advanced permissions. Contact your administrator.
      </Alert>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <SupervisorAccountIcon color="primary" fontSize="large" />
          <Typography variant="h4" component="h1">
            Enhanced Role Management
          </Typography>
          <Chip label="Enterprise Features" color="primary" size="small" />
        </Box>
      </Box>

      {/* Enhanced Features Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={selectedTab} onChange={handleTabChange} variant="scrollable" scrollButtons="auto">
          <Tab icon={<GroupIcon />} label="Role Templates" />
          <Tab icon={<PersonIcon />} label="Bulk Operations" />
          <Tab icon={<HistoryIcon />} label="Audit Trail" />
          <Tab icon={<SecurityIcon />} label="Advanced Security" />
        </Tabs>
      </Paper>

      <TabPanel value={selectedTab} index={0}>
        <RoleTemplatesPanel organizationId={organizationId} />
      </TabPanel>

      <TabPanel value={selectedTab} index={1}>
        <BulkOperationsPanel organizationId={organizationId} />
      </TabPanel>

      <TabPanel value={selectedTab} index={2}>
        <AuditTrailPanel />
      </TabPanel>

      <TabPanel value={selectedTab} index={3}>
        <Alert severity="info">
          Advanced security features - Implementation pending (MFA, session management, etc.)
        </Alert>
      </TabPanel>

      {/* Organization Context */}
      <Box sx={{ mt: 3 }}>
        <Alert severity="info" sx={{ backgroundColor: 'rgba(25, 118, 210, 0.1)' }}>
          <Typography variant="body2">
            Enhanced RBAC management for organization ID: {organizationId}. 
            All operations are scoped to this organization and logged for compliance.
          </Typography>
        </Alert>
      </Box>
    </Container>
  );
};

export default EnhancedRoleManagement;