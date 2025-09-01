import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Tab,
  Tabs,
  Grid,
  Chip,
  Alert,
  IconButton,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction
} from '@mui/material';
import {
  Preview,
  Code,
  Send,
  Save,
  Refresh,
  Info,
  ContentCopy,
  Delete,
  Add
} from '@mui/icons-material';
import { toast } from 'react-toastify';
interface EmailTemplate {
  id: number;
  name: string;
  description?: string;
  template_type: string;
  channel: string;
  subject: string;
  body: string;
  html_body?: string;
  trigger_event?: string;
  variables: string[];
  is_active: boolean;
}
interface EmailTemplateEditorProps {
  open: boolean;
  onClose: () => void;
  template?: EmailTemplate | null;
  onSave: (template: Partial<EmailTemplate>) => void;
  onTest?: (template: Partial<EmailTemplate>) => void;
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
      id={`template-tabpanel-${index}`}
      aria-labelledby={`template-tab-${index}`}
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
const EmailTemplateEditor: React.FC<EmailTemplateEditorProps> = ({
  open,
  onClose,
  template,
  onSave,
  onTest
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState<Partial<EmailTemplate>>({
    name: template?.name || '',
    description: template?.description || '',
    template_type: template?.template_type || 'exhibition_intro',
    channel: template?.channel || 'email',
    subject: template?.subject || '',
    body: template?.body || '',
    html_body: template?.html_body || '',
    trigger_event: template?.trigger_event || '',
    variables: template?.variables || [],
    is_active: template?.is_active ?? true
  });
  const [newVariable, setNewVariable] = useState('');
const [previewData,] = useState<{ [key: string]: string }>({
    prospect_name: 'John Smith',
    company_name: 'TechCorp Solutions',
    exhibition_name: 'Tech Expo 2024',
    exhibition_location: 'Convention Center',
    contact_person: 'Sarah Johnson',
    contact_email: 'sarah@yourcompany.com',
    contact_phone: '+1-555-0123'
  });
  const templateTypes = [
    { value: 'exhibition_intro', label: 'Exhibition Introduction' },
    { value: 'follow_up', label: 'Follow-up Email' },
    { value: 'appointment_reminder', label: 'Appointment Reminder' },
    { value: 'thank_you', label: 'Thank You Note' },
    { value: 'proposal_sent', label: 'Proposal Sent' },
    { value: 'meeting_request', label: 'Meeting Request' }
  ];
  const availableVariables = [
    'prospect_name',
    'company_name',
    'designation',
    'exhibition_name',
    'exhibition_location',
    'contact_person',
    'contact_email',
    'contact_phone',
    'follow_up_date',
    'meeting_time',
    'proposal_link'
  ];
  const defaultTemplates = {
    exhibition_intro: {
      subject: 'Great meeting you at {{exhibition_name}}!',
      body: `Hi {{prospect_name}},
It was wonderful meeting you at {{exhibition_name}} in {{exhibition_location}}. I enjoyed our conversation about {{company_name}} and would love to continue our discussion.
I believe our solutions could be a great fit for your needs. Would you be interested in scheduling a brief call to explore how we can help {{company_name}} achieve its goals?
Best regards,
{{contact_person}}
{{contact_email}}
{{contact_phone}}`,
      html_body: `<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <h2 style="color: #2196F3;">Great meeting you at {{exhibition_name}}!</h2>
  <p>Hi <strong>{{prospect_name}}</strong>,</p>
  <p>It was wonderful meeting you at <strong>{{exhibition_name}}</strong> in {{exhibition_location}}. I enjoyed our conversation about <strong>{{company_name}}</strong> and would love to continue our discussion.</p>
  <p>I believe our solutions could be a great fit for your needs. Would you be interested in scheduling a brief call to explore how we can help {{company_name}} achieve its goals?</p>
  <div style="margin: 20px 0; padding: 15px; background-color: #f5f5f5; border-radius: 5px;">
    <p style="margin: 0;"><strong>{{contact_person}}</strong><br>
    📧 {{contact_email}}<br>
    📞 {{contact_phone}}</p>
  </div>
</div>`
    }
  };
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };
  const handleInputChange = (field: keyof EmailTemplate, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };
  const handleAddVariable = () => {
    if (newVariable && !formData.variables?.includes(newVariable)) {
      setFormData(prev => ({
        ...prev,
        variables: [...(prev.variables || []), newVariable]
      }));
      setNewVariable('');
    }
  };
  const handleRemoveVariable = (variable: string) => {
    setFormData(prev => ({
      ...prev,
      variables: prev.variables?.filter(v => v !== variable) || []
    }));
  };
  const insertVariable = (variable: string, field: 'subject' | 'body' | 'html_body') => {
    const variableText = `{{${variable}}}`;
    const currentValue = formData[field] || '';
    // For simplicity, just append the variable. In a real implementation,
    // you'd want to insert at cursor position
    handleInputChange(field, currentValue + variableText);
  };
  const renderPreview = (text: string, isHtml: boolean = false) => {
    let processedText = text;
    // Replace variables with preview data
    Object.entries(previewData).forEach(([key, value]) => {
      const regex = new RegExp(`{{${key}}}`, 'g');
      processedText = processedText.replace(regex, value);
    });
    if (isHtml) {
      return <div dangerouslySetInnerHTML={{ __html: processedText }} />;
    }
    return (
      <Typography component="pre" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
        {processedText}
      </Typography>
    );
  };
  const loadDefaultTemplate = () => {
    const defaultTemplate = defaultTemplates[formData.template_type as keyof typeof defaultTemplates];
    if (defaultTemplate) {
      setFormData(prev => ({
        ...prev,
        ...defaultTemplate,
        variables: [...(prev.variables || []), ...Object.keys(previewData)]
      }));
      toast.success('Default template loaded');
    }
  };
  const handleSave = () => {
    if (!formData.name || !formData.subject || !formData.body) {
      toast.error('Please fill in required fields: Name, Subject, and Body');
      return;
    }
    onSave(formData);
    toast.success('Email template saved successfully');
  };
  const handleTest = () => {
    if (onTest) {
      onTest(formData);
      toast.success('Test email sent');
    }
  };
  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="between" alignItems="center">
          <Typography variant="h6">
            {template ? 'Edit Email Template' : 'Create Email Template'}
          </Typography>
          <Box>
            <Tooltip title="Load default template">
              <IconButton onClick={loadDefaultTemplate}>
                <Refresh />
              </IconButton>
            </Tooltip>
            <Tooltip title="Template help">
              <IconButton>
                <Info />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </DialogTitle>
      <DialogContent sx={{ p: 0 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="Template Settings" />
            <Tab label="Email Content" />
            <Tab label="Variables" />
            <Tab label="Preview" />
          </Tabs>
        </Box>
        {/* Template Settings Tab */}
        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Template Name"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Template Type</InputLabel>
                <Select
                  value={formData.template_type}
                  label="Template Type"
                  onChange={(e) => handleInputChange('template_type', e.target.value)}
                >
                  {templateTypes.map(type => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Trigger Event"
                value={formData.trigger_event}
                onChange={(e) => handleInputChange('trigger_event', e.target.value)}
                helperText="When should this template be automatically sent?"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Channel</InputLabel>
                <Select
                  value={formData.channel}
                  label="Channel"
                  onChange={(e) => handleInputChange('channel', e.target.value)}
                >
                  <MenuItem value="email">Email</MenuItem>
                  <MenuItem value="sms">SMS</MenuItem>
                  <MenuItem value="push">Push Notification</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </TabPanel>
        {/* Email Content Tab */}
        <TabPanel value={activeTab} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Email Subject"
                value={formData.subject}
                onChange={(e) => handleInputChange('subject', e.target.value)}
                required
                helperText="Use {{variable_name}} for dynamic content"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Email Body (Plain Text)"
                value={formData.body}
                onChange={(e) => handleInputChange('body', e.target.value)}
                multiline
                rows={10}
                required
                helperText="Plain text version of the email"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Email Body (HTML)"
                value={formData.html_body}
                onChange={(e) => handleInputChange('html_body', e.target.value)}
                multiline
                rows={10}
                helperText="HTML version for rich formatting (optional)"
              />
            </Grid>
          </Grid>
        </TabPanel>
        {/* Variables Tab */}
        <TabPanel value={activeTab} index={2}>
          <Typography variant="h6" gutterBottom>
            Template Variables
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Variables allow you to personalize emails with dynamic content. Use {{variable_name}} in your template.
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Available Variables
                </Typography>
                <List dense>
                  {availableVariables.map(variable => (
                    <ListItem key={variable}>
                      <ListItemText 
                        primary={`{{${variable}}}`}
                        secondary={previewData[variable] || 'Sample data not available'}
                      />
                      <ListItemSecondaryAction>
                        <Tooltip title="Copy to clipboard">
                          <IconButton 
                            size="small"
                            onClick={() => {
                              navigator.clipboard.writeText(`{{${variable}}}`);
                              toast.success('Variable copied to clipboard');
                            }}
                          >
                            <ContentCopy />
                          </IconButton>
                        </Tooltip>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Used Variables
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
                  {formData.variables?.map(variable => (
                    <Chip
                      key={variable}
                      label={variable}
                      onDelete={() => handleRemoveVariable(variable)}
                      size="small"
                    />
                  ))}
                </Box>
                <Box display="flex" gap={1}>
                  <TextField
                    size="small"
                    label="Add Variable"
                    value={newVariable}
                    onChange={(e) => setNewVariable(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddVariable()}
                  />
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<Add />}
                    onClick={handleAddVariable}
                  >
                    Add
                  </Button>
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>
        {/* Preview Tab */}
        <TabPanel value={activeTab} index={3}>
          <Typography variant="h6" gutterBottom>
            Email Preview
          </Typography>
          <Alert severity="info" sx={{ mb: 3 }}>
            This preview shows how the email will look with sample data.
          </Alert>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
              Subject: {renderPreview(formData.subject || '')}
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Box sx={{ minHeight: 200 }}>
              {activeTab === 3 && formData.html_body ? (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    HTML Preview:
                  </Typography>
                  {renderPreview(formData.html_body, true)}
                </Box>
              ) : (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Plain Text Preview:
                  </Typography>
                  {renderPreview(formData.body || '')}
                </Box>
              )}
            </Box>
          </Paper>
          <Box display="flex" gap={2}>
            <Button
              variant="outlined"
              startIcon={<Send />}
              onClick={handleTest}
              disabled={!onTest}
            >
              Send Test Email
            </Button>
            <Button
              variant="outlined"
              startIcon={<Preview />}
              onClick={() => {
                // Toggle between HTML and plain text preview
                // This is just a demo action
                toast.info('Preview mode toggled');
              }}
            >
              Toggle Preview Mode
            </Button>
          </Box>
        </TabPanel>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>
          Cancel
        </Button>
        <Button
          variant="contained"
          startIcon={<Save />}
          onClick={handleSave}
        >
          {template ? 'Update Template' : 'Create Template'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
export default EmailTemplateEditor;