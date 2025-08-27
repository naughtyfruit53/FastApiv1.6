// src/components/SendNotification.tsx
// Component for sending notifications to customers and users

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Autocomplete,
  Chip,
  Alert,
  CircularProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab
} from '@mui/material';
import {
  Send,
  Person,
  Group,
  Email,
  Sms,
  NotificationImportant,
  Notifications,
  Preview,
  CheckCircle,
  Error
} from '@mui/icons-material';
import { useQuery, useMutation } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import {
  getNotificationTemplates,
  sendNotification,
  sendBulkNotification,
  testNotificationTemplate,
  NotificationTemplate,
  NotificationSendRequest,
  BulkNotificationRequest,
  NOTIFICATION_CHANNELS,
  RECIPIENT_TYPES,
  BULK_RECIPIENT_TYPES,
  getChannelDisplayName,
  getTemplateTypeDisplayName,
  notificationQueryKeys
} from '../services/notificationService';
import { getAllEntities } from '../services/entityService';

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
      id={`send-tabpanel-${index}`}
      aria-labelledby={`send-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const SendNotification: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [previewContent, setPreviewContent] = useState<any>(null);
  
  // Single notification form state
  const [singleForm, setSingleForm] = useState({
    template_id: '',
    recipient_type: 'customer' as 'customer' | 'user',
    recipient_id: '',
    channel: 'email',
    variables: {} as Record<string, string>,
    override_subject: '',
    override_content: ''
  });

  // Bulk notification form state
  const [bulkForm, setBulkForm] = useState({
    template_id: '',
    subject: '',
    content: '',
    channel: 'email',
    recipient_type: 'customers' as 'customers' | 'segment' | 'users',
    recipient_ids: [] as number[],
    segment_name: '',
    variables: {} as Record<string, string>
  });

  // Get templates
  const { 
    data: templates = [], 
    isLoading: templatesLoading 
  } = useQuery({
    queryKey: notificationQueryKeys.templates(),
    queryFn: () => getNotificationTemplates({ is_active: true }),
  });

  // Get entities (customers/users)
  const { 
    data: entities = [], 
    isLoading: entitiesLoading 
  } = useQuery({
    queryKey: ['entities'],
    queryFn: getAllEntities,
  });

  // Send single notification mutation
  const sendSingleMutation = useMutation({
    mutationFn: sendNotification,
    onSuccess: (data) => {
      toast.success('Notification sent successfully');
      resetSingleForm();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to send notification');
    }
  });

  // Send bulk notification mutation
  const sendBulkMutation = useMutation({
    mutationFn: sendBulkNotification,
    onSuccess: (data) => {
      toast.success(`Bulk notification sent: ${data.successful_sends}/${data.total_recipients} successful`);
      if (data.errors.length > 0) {
        toast.warning(`${data.failed_sends} notifications failed`);
      }
      resetBulkForm();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to send bulk notification');
    }
  });

  // Preview mutation
  const previewMutation = useMutation({
    mutationFn: ({ id, testData }: { id: number; testData: any }) =>
      testNotificationTemplate(id, testData),
    onSuccess: (data) => {
      setPreviewContent(data);
      setIsPreviewOpen(true);
    },
    onError: (error: any) => {
      toast.error('Failed to generate preview');
    }
  });

  const resetSingleForm = () => {
    setSingleForm({
      template_id: '',
      recipient_type: 'customer',
      recipient_id: '',
      channel: 'email',
      variables: {},
      override_subject: '',
      override_content: ''
    });
  };

  const resetBulkForm = () => {
    setBulkForm({
      template_id: '',
      subject: '',
      content: '',
      channel: 'email',
      recipient_type: 'customers',
      recipient_ids: [],
      segment_name: '',
      variables: {}
    });
  };

  const handleSendSingle = () => {
    if (!singleForm.recipient_id) {
      toast.error('Please select a recipient');
      return;
    }

    if (!singleForm.template_id && !singleForm.override_content) {
      toast.error('Please select a template or provide custom content');
      return;
    }

    const request: NotificationSendRequest = {
      template_id: singleForm.template_id ? parseInt(singleForm.template_id) : undefined,
      recipient_type: singleForm.recipient_type,
      recipient_id: parseInt(singleForm.recipient_id),
      channel: singleForm.channel,
      variables: Object.keys(singleForm.variables).length > 0 ? singleForm.variables : undefined,
      override_subject: singleForm.override_subject || undefined,
      override_content: singleForm.override_content || undefined
    };

    sendSingleMutation.mutate(request);
  };

  const handleSendBulk = () => {
    if (bulkForm.recipient_type === 'customers' && bulkForm.recipient_ids.length === 0) {
      toast.error('Please select customers');
      return;
    }

    if (bulkForm.recipient_type === 'segment' && !bulkForm.segment_name) {
      toast.error('Please enter segment name');
      return;
    }

    if (!bulkForm.template_id && !bulkForm.content) {
      toast.error('Please select a template or provide custom content');
      return;
    }

    const request: BulkNotificationRequest = {
      template_id: bulkForm.template_id ? parseInt(bulkForm.template_id) : undefined,
      subject: bulkForm.subject || undefined,
      content: bulkForm.content,
      channel: bulkForm.channel,
      recipient_type: bulkForm.recipient_type,
      recipient_ids: bulkForm.recipient_ids.length > 0 ? bulkForm.recipient_ids : undefined,
      segment_name: bulkForm.segment_name || undefined,
      variables: Object.keys(bulkForm.variables).length > 0 ? bulkForm.variables : undefined
    };

    sendBulkMutation.mutate(request);
  };

  const handlePreview = (isForBulk: boolean = false) => {
    const templateId = isForBulk ? bulkForm.template_id : singleForm.template_id;
    const variables = isForBulk ? bulkForm.variables : singleForm.variables;

    if (!templateId) {
      toast.error('Please select a template to preview');
      return;
    }

    previewMutation.mutate({
      id: parseInt(templateId),
      testData: { variables }
    });
  };

  const selectedTemplate = templates.find(t => 
    t.id === parseInt(selectedTab === 0 ? singleForm.template_id : bulkForm.template_id)
  );

  // Filter entities based on recipient type
  const customers = entities.filter(e => e.type === 'Customer');
  const users = entities.filter(e => e.type === 'User');

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'email': return <Email />;
      case 'sms': return <Sms />;
      case 'push': return <NotificationImportant />;
      case 'in_app': return <Notifications />;
      default: return <Notifications />;
    }
  };

  return (
    <Box>
      <Card>
        <CardContent>
          <Typography variant="h5" component="h2" mb={3}>
            Send Notifications
          </Typography>

          <Tabs 
            value={selectedTab} 
            onChange={(_, newValue) => setSelectedTab(newValue)}
            sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}
          >
            <Tab 
              label="Single Notification" 
              icon={<Person />}
              iconPosition="start"
            />
            <Tab 
              label="Bulk Notification" 
              icon={<Group />}
              iconPosition="start"
            />
          </Tabs>

          {/* Single Notification Tab */}
          <TabPanel value={selectedTab} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Template (Optional)</InputLabel>
                  <Select
                    value={singleForm.template_id}
                    label="Template (Optional)"
                    onChange={(e) => setSingleForm({ ...singleForm, template_id: e.target.value })}
                  >
                    <MenuItem value="">Custom Message</MenuItem>
                    {templates.map(template => (
                      <MenuItem key={template.id} value={template.id.toString()}>
                        {template.name} ({getChannelDisplayName(template.channel as any)})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Channel</InputLabel>
                  <Select
                    value={singleForm.channel}
                    label="Channel"
                    onChange={(e) => setSingleForm({ ...singleForm, channel: e.target.value })}
                  >
                    {NOTIFICATION_CHANNELS.map(channel => (
                      <MenuItem key={channel} value={channel}>
                        <Box display="flex" alignItems="center" gap={1}>
                          {getChannelIcon(channel)}
                          {getChannelDisplayName(channel)}
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Recipient Type</InputLabel>
                  <Select
                    value={singleForm.recipient_type}
                    label="Recipient Type"
                    onChange={(e) => setSingleForm({ 
                      ...singleForm, 
                      recipient_type: e.target.value as any,
                      recipient_id: '' 
                    })}
                  >
                    <MenuItem value="customer">Customer</MenuItem>
                    <MenuItem value="user">User</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <Autocomplete
                  options={singleForm.recipient_type === 'customer' ? customers : users}
                  getOptionLabel={(option) => option.name}
                  value={entities.find(e => e.id.toString() === singleForm.recipient_id) || null}
                  onChange={(_, value) => setSingleForm({ 
                    ...singleForm, 
                    recipient_id: value?.id.toString() || '' 
                  })}
                  renderInput={(params) => (
                    <TextField 
                      {...params} 
                      label={`Select ${singleForm.recipient_type}`}
                      margin="normal"
                      fullWidth
                    />
                  )}
                />
              </Grid>

              {!singleForm.template_id && (
                <>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Subject"
                      value={singleForm.override_subject}
                      onChange={(e) => setSingleForm({ ...singleForm, override_subject: e.target.value })}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Message Content"
                      value={singleForm.override_content}
                      onChange={(e) => setSingleForm({ ...singleForm, override_content: e.target.value })}
                      multiline
                      rows={4}
                      margin="normal"
                      required
                    />
                  </Grid>
                </>
              )}

              {selectedTemplate && selectedTemplate.variables && (
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>
                    Template Variables
                  </Typography>
                  <Grid container spacing={2}>
                    {selectedTemplate.variables.map(variable => (
                      <Grid item xs={12} sm={6} key={variable}>
                        <TextField
                          fullWidth
                          label={variable}
                          value={singleForm.variables[variable] || ''}
                          onChange={(e) => setSingleForm({
                            ...singleForm,
                            variables: {
                              ...singleForm.variables,
                              [variable]: e.target.value
                            }
                          })}
                        />
                      </Grid>
                    ))}
                  </Grid>
                </Grid>
              )}

              <Grid item xs={12}>
                <Box display="flex" gap={2}>
                  <Button
                    variant="contained"
                    startIcon={<Send />}
                    onClick={handleSendSingle}
                    disabled={sendSingleMutation.isPending}
                  >
                    Send Notification
                  </Button>
                  {singleForm.template_id && (
                    <Button
                      variant="outlined"
                      startIcon={<Preview />}
                      onClick={() => handlePreview(false)}
                      disabled={previewMutation.isPending}
                    >
                      Preview
                    </Button>
                  )}
                </Box>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Bulk Notification Tab */}
          <TabPanel value={selectedTab} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Template (Optional)</InputLabel>
                  <Select
                    value={bulkForm.template_id}
                    label="Template (Optional)"
                    onChange={(e) => setBulkForm({ ...bulkForm, template_id: e.target.value })}
                  >
                    <MenuItem value="">Custom Message</MenuItem>
                    {templates.map(template => (
                      <MenuItem key={template.id} value={template.id.toString()}>
                        {template.name} ({getChannelDisplayName(template.channel as any)})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Channel</InputLabel>
                  <Select
                    value={bulkForm.channel}
                    label="Channel"
                    onChange={(e) => setBulkForm({ ...bulkForm, channel: e.target.value })}
                  >
                    {NOTIFICATION_CHANNELS.map(channel => (
                      <MenuItem key={channel} value={channel}>
                        <Box display="flex" alignItems="center" gap={1}>
                          {getChannelIcon(channel)}
                          {getChannelDisplayName(channel)}
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Recipient Type</InputLabel>
                  <Select
                    value={bulkForm.recipient_type}
                    label="Recipient Type"
                    onChange={(e) => setBulkForm({ 
                      ...bulkForm, 
                      recipient_type: e.target.value as any,
                      recipient_ids: [],
                      segment_name: ''
                    })}
                  >
                    <MenuItem value="customers">Select Customers</MenuItem>
                    <MenuItem value="segment">Customer Segment</MenuItem>
                    <MenuItem value="users">Select Users</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              {bulkForm.recipient_type === 'customers' && (
                <Grid item xs={12}>
                  <Autocomplete
                    multiple
                    options={customers}
                    getOptionLabel={(option) => option.name}
                    value={customers.filter(c => bulkForm.recipient_ids.includes(c.id))}
                    onChange={(_, value) => setBulkForm({ 
                      ...bulkForm, 
                      recipient_ids: value.map(v => v.id) 
                    })}
                    renderInput={(params) => (
                      <TextField 
                        {...params} 
                        label="Select Customers"
                        margin="normal"
                        fullWidth
                      />
                    )}
                    renderTags={(value, getTagProps) =>
                      value.map((option, index) => (
                        <Chip
                          variant="outlined"
                          label={option.name}
                          {...getTagProps({ index })}
                          key={option.id}
                        />
                      ))
                    }
                  />
                </Grid>
              )}

              {bulkForm.recipient_type === 'segment' && (
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Segment Name"
                    value={bulkForm.segment_name}
                    onChange={(e) => setBulkForm({ ...bulkForm, segment_name: e.target.value })}
                    margin="normal"
                    helperText="e.g., 'vip', 'premium', 'new_customers'"
                  />
                </Grid>
              )}

              {bulkForm.recipient_type === 'users' && (
                <Grid item xs={12}>
                  <Autocomplete
                    multiple
                    options={users}
                    getOptionLabel={(option) => option.name}
                    value={users.filter(u => bulkForm.recipient_ids.includes(u.id))}
                    onChange={(_, value) => setBulkForm({ 
                      ...bulkForm, 
                      recipient_ids: value.map(v => v.id) 
                    })}
                    renderInput={(params) => (
                      <TextField 
                        {...params} 
                        label="Select Users"
                        margin="normal"
                        fullWidth
                      />
                    )}
                    renderTags={(value, getTagProps) =>
                      value.map((option, index) => (
                        <Chip
                          variant="outlined"
                          label={option.name}
                          {...getTagProps({ index })}
                          key={option.id}
                        />
                      ))
                    }
                  />
                </Grid>
              )}

              {!bulkForm.template_id && (
                <>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Subject"
                      value={bulkForm.subject}
                      onChange={(e) => setBulkForm({ ...bulkForm, subject: e.target.value })}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Message Content"
                      value={bulkForm.content}
                      onChange={(e) => setBulkForm({ ...bulkForm, content: e.target.value })}
                      multiline
                      rows={4}
                      margin="normal"
                      required
                    />
                  </Grid>
                </>
              )}

              <Grid item xs={12}>
                <Box display="flex" gap={2}>
                  <Button
                    variant="contained"
                    startIcon={<Send />}
                    onClick={handleSendBulk}
                    disabled={sendBulkMutation.isPending}
                  >
                    Send Bulk Notification
                  </Button>
                  {bulkForm.template_id && (
                    <Button
                      variant="outlined"
                      startIcon={<Preview />}
                      onClick={() => handlePreview(true)}
                      disabled={previewMutation.isPending}
                    >
                      Preview
                    </Button>
                  )}
                </Box>
              </Grid>
            </Grid>
          </TabPanel>
        </CardContent>
      </Card>

      {/* Preview Modal */}
      <Dialog open={isPreviewOpen} onClose={() => setIsPreviewOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Template Preview</DialogTitle>
        <DialogContent>
          {previewContent && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {previewContent.template_name} ({getChannelDisplayName(previewContent.channel)})
              </Typography>
              {previewContent.test_subject && (
                <Box mb={2}>
                  <Typography variant="subtitle2" color="text.secondary">Subject:</Typography>
                  <Typography>{previewContent.test_subject}</Typography>
                </Box>
              )}
              <Box mb={2}>
                <Typography variant="subtitle2" color="text.secondary">Content:</Typography>
                <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Typography style={{ whiteSpace: 'pre-wrap' }}>
                    {previewContent.test_content}
                  </Typography>
                </Paper>
              </Box>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">Variables used:</Typography>
                <Box display="flex" gap={1} flexWrap="wrap" mt={1}>
                  {Object.entries(previewContent.variables_used).map(([key, value]) => (
                    <Chip 
                      key={key} 
                      label={`${key}: ${value}`} 
                      size="small" 
                      variant="outlined" 
                    />
                  ))}
                </Box>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsPreviewOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SendNotification;