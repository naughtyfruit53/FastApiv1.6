// src/components/NotificationTemplates.tsx
// Component for managing notification templates

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Switch,
  FormControlLabel,
  Tabs,
  Tab
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  PlayArrow,
  Notifications,
  Email,
  Sms,
  NotificationImportant,
  Assignment
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import {
  getNotificationTemplates,
  createNotificationTemplate,
  updateNotificationTemplate,
  deleteNotificationTemplate,
  testNotificationTemplate,
  NotificationTemplate,
  NotificationTemplateCreate,
  NotificationTemplateUpdate,
  NOTIFICATION_CHANNELS,
  TEMPLATE_TYPES,
  getChannelDisplayName,
  getTemplateTypeDisplayName,
  notificationQueryKeys
} from '../services/notificationService';

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
      id={`template-tabpanel-${index}`}
      aria-labelledby={`template-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const NotificationTemplates: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [editingTemplate, setEditingTemplate] = useState<NotificationTemplate | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [templateToDelete, setTemplateToDelete] = useState<NotificationTemplate | null>(null);
  const [testingTemplate, setTestingTemplate] = useState<NotificationTemplate | null>(null);
  
  const queryClient = useQueryClient();

  // Form state for create/edit
  const [formData, setFormData] = useState<NotificationTemplateCreate>({
    name: '',
    description: '',
    template_type: 'appointment_reminder',
    channel: 'email',
    subject: '',
    body: '',
    html_body: '',
    trigger_event: '',
    variables: [],
    is_active: true
  });

  // Get templates data
  const { 
    data: templates = [], 
    isLoading, 
    error 
  } = useQuery({
    queryKey: notificationQueryKeys.templates(),
    queryFn: () => getNotificationTemplates(),
  });

  // Create template mutation
  const createMutation = useMutation({
    mutationFn: createNotificationTemplate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationQueryKeys.templates() });
      setIsCreateModalOpen(false);
      resetForm();
      toast.success('Template created successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create template');
    }
  });

  // Update template mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: NotificationTemplateUpdate }) =>
      updateNotificationTemplate(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationQueryKeys.templates() });
      setEditingTemplate(null);
      resetForm();
      toast.success('Template updated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update template');
    }
  });

  // Delete template mutation
  const deleteMutation = useMutation({
    mutationFn: deleteNotificationTemplate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: notificationQueryKeys.templates() });
      setIsDeleteModalOpen(false);
      setTemplateToDelete(null);
      toast.success('Template deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete template');
    }
  });

  // Test template mutation
  const testMutation = useMutation({
    mutationFn: ({ id, testData }: { id: number; testData: any }) =>
      testNotificationTemplate(id, testData),
    onSuccess: (data) => {
      toast.success('Template test completed successfully');
      console.log('Test result:', data);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to test template');
    }
  });

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      template_type: 'appointment_reminder',
      channel: 'email',
      subject: '',
      body: '',
      html_body: '',
      trigger_event: '',
      variables: [],
      is_active: true
    });
  };

  const handleEdit = (template: NotificationTemplate) => {
    setEditingTemplate(template);
    setFormData({
      name: template.name,
      description: template.description || '',
      template_type: template.template_type,
      channel: template.channel,
      subject: template.subject || '',
      body: template.body,
      html_body: template.html_body || '',
      trigger_event: template.trigger_event || '',
      variables: template.variables || [],
      is_active: template.is_active
    });
    setIsCreateModalOpen(true);
  };

  const handleSubmit = () => {
    if (editingTemplate) {
      updateMutation.mutate({ id: editingTemplate.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleDelete = (template: NotificationTemplate) => {
    setTemplateToDelete(template);
    setIsDeleteModalOpen(true);
  };

  const confirmDelete = () => {
    if (templateToDelete) {
      deleteMutation.mutate(templateToDelete.id);
    }
  };

  const handleTest = (template: NotificationTemplate) => {
    testMutation.mutate({
      id: template.id,
      testData: {
        variables: {
          customer_name: 'John Doe',
          appointment_date: '2024-01-15 10:00 AM',
          service_type: 'AC Repair'
        }
      }
    });
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'email':
        return <Email />;
      case 'sms':
        return <Sms />;
      case 'push':
        return <NotificationImportant />;
      case 'in_app':
        return <Notifications />;
      default:
        return <Assignment />;
    }
  };

  // Filter templates by channel for tabs
  const emailTemplates = templates.filter(t => t.channel === 'email');
  const smsTemplates = templates.filter(t => t.channel === 'sms');
  const pushTemplates = templates.filter(t => t.channel === 'push');
  const inAppTemplates = templates.filter(t => t.channel === 'in_app');

  const TemplateTable: React.FC<{ templates: NotificationTemplate[] }> = ({ templates }) => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Channel</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Variables</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {templates.map((template) => (
            <TableRow key={template.id}>
              <TableCell>
                <Box>
                  <Typography variant="subtitle2">{template.name}</Typography>
                  {template.description && (
                    <Typography variant="caption" color="text.secondary">
                      {template.description}
                    </Typography>
                  )}
                </Box>
              </TableCell>
              <TableCell>
                <Chip 
                  label={getTemplateTypeDisplayName(template.template_type as any)} 
                  size="small"
                  variant="outlined"
                />
              </TableCell>
              <TableCell>
                <Box display="flex" alignItems="center" gap={1}>
                  {getChannelIcon(template.channel)}
                  {getChannelDisplayName(template.channel as any)}
                </Box>
              </TableCell>
              <TableCell>
                <Chip 
                  label={template.is_active ? 'Active' : 'Inactive'}
                  color={template.is_active ? 'success' : 'default'}
                  size="small"
                />
              </TableCell>
              <TableCell>
                {template.variables && template.variables.length > 0 && (
                  <Tooltip title={template.variables.join(', ')}>
                    <Chip 
                      label={`${template.variables.length} variables`} 
                      size="small"
                      variant="outlined"
                    />
                  </Tooltip>
                )}
              </TableCell>
              <TableCell>
                <Box display="flex" gap={1}>
                  <Tooltip title="Test Template">
                    <IconButton 
                      size="small" 
                      onClick={() => handleTest(template)}
                      disabled={testMutation.isPending}
                    >
                      <PlayArrow />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit Template">
                    <IconButton size="small" onClick={() => handleEdit(template)}>
                      <Edit />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete Template">
                    <IconButton 
                      size="small" 
                      onClick={() => handleDelete(template)}
                      color="error"
                    >
                      <Delete />
                    </IconButton>
                  </Tooltip>
                </Box>
              </TableCell>
            </TableRow>
          ))}
          {templates.length === 0 && (
            <TableRow>
              <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                <Typography color="text.secondary">
                  No templates found for this channel
                </Typography>
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );

  if (error) {
    return (
      <Alert severity="error">
        Failed to load notification templates. Please try again.
      </Alert>
    );
  }

  return (
    <Box>
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5" component="h2">
              Notification Templates
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setIsCreateModalOpen(true)}
            >
              Create Template
            </Button>
          </Box>

          {isLoading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : (
            <Box>
              <Tabs 
                value={selectedTab} 
                onChange={(_, newValue) => setSelectedTab(newValue)}
                sx={{ borderBottom: 1, borderColor: 'divider' }}
              >
                <Tab 
                  label={`Email (${emailTemplates.length})`} 
                  icon={<Email />}
                  iconPosition="start"
                />
                <Tab 
                  label={`SMS (${smsTemplates.length})`} 
                  icon={<Sms />}
                  iconPosition="start"
                />
                <Tab 
                  label={`Push (${pushTemplates.length})`} 
                  icon={<NotificationImportant />}
                  iconPosition="start"
                />
                <Tab 
                  label={`In-App (${inAppTemplates.length})`} 
                  icon={<Notifications />}
                  iconPosition="start"
                />
              </Tabs>

              <TabPanel value={selectedTab} index={0}>
                <TemplateTable templates={emailTemplates} />
              </TabPanel>
              <TabPanel value={selectedTab} index={1}>
                <TemplateTable templates={smsTemplates} />
              </TabPanel>
              <TabPanel value={selectedTab} index={2}>
                <TemplateTable templates={pushTemplates} />
              </TabPanel>
              <TabPanel value={selectedTab} index={3}>
                <TemplateTable templates={inAppTemplates} />
              </TabPanel>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Create/Edit Template Modal */}
      <Dialog 
        open={isCreateModalOpen} 
        onClose={() => setIsCreateModalOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingTemplate ? 'Edit Template' : 'Create Template'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Template Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Template Type</InputLabel>
                <Select
                  value={formData.template_type}
                  label="Template Type"
                  onChange={(e) => setFormData({ ...formData, template_type: e.target.value })}
                >
                  {TEMPLATE_TYPES.map(type => (
                    <MenuItem key={type} value={type}>
                      {getTemplateTypeDisplayName(type)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Channel</InputLabel>
                <Select
                  value={formData.channel}
                  label="Channel"
                  onChange={(e) => setFormData({ ...formData, channel: e.target.value })}
                >
                  {NOTIFICATION_CHANNELS.map(channel => (
                    <MenuItem key={channel} value={channel}>
                      {getChannelDisplayName(channel)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  />
                }
                label="Active"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                multiline
                rows={2}
              />
            </Grid>
            {formData.channel === 'email' && (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Subject"
                  value={formData.subject}
                  onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                />
              </Grid>
            )}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Message Body"
                value={formData.body}
                onChange={(e) => setFormData({ ...formData, body: e.target.value })}
                multiline
                rows={4}
                required
                helperText="Use {variable_name} for dynamic content (e.g., {customer_name}, {appointment_date})"
              />
            </Grid>
            {formData.channel === 'email' && (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="HTML Body (Optional)"
                  value={formData.html_body}
                  onChange={(e) => setFormData({ ...formData, html_body: e.target.value })}
                  multiline
                  rows={4}
                  helperText="HTML version of the email for rich formatting"
                />
              </Grid>
            )}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Trigger Event (Optional)"
                value={formData.trigger_event}
                onChange={(e) => setFormData({ ...formData, trigger_event: e.target.value })}
                helperText="Event that automatically triggers this notification (e.g., customer_interaction, appointment_scheduled)"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsCreateModalOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleSubmit}
            variant="contained"
            disabled={createMutation.isPending || updateMutation.isPending}
          >
            {editingTemplate ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Modal */}
      <Dialog open={isDeleteModalOpen} onClose={() => setIsDeleteModalOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the template "{templateToDelete?.name}"?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDeleteModalOpen(false)}>Cancel</Button>
          <Button 
            onClick={confirmDelete}
            color="error"
            variant="contained"
            disabled={deleteMutation.isPending}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default NotificationTemplates;