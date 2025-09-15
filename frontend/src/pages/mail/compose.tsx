// frontend/src/pages/mail/compose.tsx
import React, { useState, useRef } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Toolbar,
  AppBar,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Switch,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
} from "@mui/material";
import {
  Send,
  Save,
  AttachFile,
  Close,
  FormatBold,
  FormatItalic,
  FormatUnderlined,
  Delete,
  InsertEmoticon,
  AccountBox,
  ExpandMore,
  ExpandLess,
} from "@mui/icons-material";
import { useRouter } from "next/router";
import { useForm, Controller } from "react-hook-form";

interface EmailFormData {
  to: string;
  cc: string;
  bcc: string;
  subject: string;
  body: string;
  priority: "low" | "normal" | "high" | "urgent";
  schedule_send?: Date;
}

interface Attachment {
  id: string;
  name: string;
  size: number;
  type: string;
  file?: File;
}

interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  body: string;
}

const ComposePage: React.FC = () => {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [showCcBcc, setShowCcBcc] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [scheduleSend, setScheduleSend] = useState(false);
  const [richTextMode, setRichTextMode] = useState(false);

  const { control, handleSubmit, formState: { errors }, watch, setValue, reset } = useForm<EmailFormData>({
    defaultValues: {
      to: "",
      cc: "",
      bcc: "",
      subject: "",
      body: "",
      priority: "normal",
    },
  });

  // Mock templates for demo
  React.useEffect(() => {
    const mockTemplates: EmailTemplate[] = [
      {
        id: "1",
        name: "Meeting Request",
        subject: "Meeting Request: [Topic]",
        body: "Dear [Name],\n\nI would like to schedule a meeting to discuss [topic]. Please let me know your availability.\n\nBest regards,\n[Your Name]",
      },
      {
        id: "2",
        name: "Follow-up",
        subject: "Follow-up on [Topic]",
        body: "Hi [Name],\n\nI wanted to follow up on our previous conversation about [topic]. Please let me know if you need any additional information.\n\nBest regards,\n[Your Name]",
      },
      {
        id: "3",
        name: "Invoice",
        subject: "Invoice #[Invoice Number]",
        body: "Dear [Client Name],\n\nPlease find attached invoice #[Invoice Number] for [services/products]. Payment is due within [payment terms].\n\nThank you for your business.\n\nBest regards,\n[Your Name]",
      },
    ];
    setTemplates(mockTemplates);
  }, []);

  const handleSend = async (data: EmailFormData) => {
    try {
      setLoading(true);
      setError(null);
      
      const emailData = {
        ...data,
        to: data.to.split(',').map(email => email.trim()).filter(Boolean),
        cc: data.cc ? data.cc.split(',').map(email => email.trim()).filter(Boolean) : [],
        bcc: data.bcc ? data.bcc.split(',').map(email => email.trim()).filter(Boolean) : [],
        attachments: attachments.map(att => att.id),
      };

      console.log('Sending email:', emailData);
      
      // TODO: Implement actual API call
      // const response = await api.post('/api/v1/email/send', emailData);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setSuccess('Email sent successfully!');
      reset();
      setAttachments([]);
      
      setTimeout(() => {
        router.push('/mail/sent');
      }, 2000);
      
    } catch (err: any) {
      console.error('Error sending email:', err);
      setError('Failed to send email. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveDraft = async (data: EmailFormData) => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Saving draft:', data);
      
      // TODO: Implement actual API call
      // const response = await api.post('/api/v1/email/drafts', data);
      
      setSuccess('Draft saved successfully!');
    } catch (err: any) {
      console.error('Error saving draft:', err);
      setError('Failed to save draft. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    Array.from(files).forEach((file) => {
      const newAttachment: Attachment = {
        id: `att-${Date.now()}-${Math.random()}`,
        name: file.name,
        size: file.size,
        type: file.type,
        file,
      };
      setAttachments(prev => [...prev, newAttachment]);
    });

    // Clear the input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleRemoveAttachment = (attachmentId: string) => {
    setAttachments(prev => prev.filter(att => att.id !== attachmentId));
  };

  const handleUseTemplate = (template: EmailTemplate) => {
    setValue('subject', template.subject);
    setValue('body', template.body);
    setShowTemplates(false);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "urgent": return "error";
      case "high": return "warning";
      case "normal": return "default";
      case "low": return "info";
      default: return "default";
    }
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Compose Email
          </Typography>
          <Button
            variant="outlined"
            startIcon={<Save />}
            onClick={handleSubmit(handleSaveDraft)}
            disabled={loading}
            sx={{ mr: 1 }}
          >
            Save Draft
          </Button>
          <Button
            variant="contained"
            startIcon={<Send />}
            onClick={handleSubmit(handleSend)}
            disabled={loading}
          >
            {loading ? <CircularProgress size={20} /> : 'Send'}
          </Button>
          <IconButton onClick={() => router.back()} sx={{ ml: 1 }}>
            <Close />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Alerts */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ m: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ m: 2 }}>
          {success}
        </Alert>
      )}

      {/* Main Content */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        <Card>
          <CardContent>
            <form onSubmit={handleSubmit(handleSend)}>
              {/* Recipients */}
              <Box sx={{ mb: 2 }}>
                <Controller
                  name="to"
                  control={control}
                  rules={{ required: 'To field is required' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="To"
                      fullWidth
                      placeholder="recipient@example.com, another@example.com"
                      error={!!errors.to}
                      helperText={errors.to?.message || "Separate multiple emails with commas"}
                      variant="outlined"
                    />
                  )}
                />
                
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  <Button
                    size="small"
                    onClick={() => setShowCcBcc(!showCcBcc)}
                    endIcon={showCcBcc ? <ExpandLess /> : <ExpandMore />}
                  >
                    CC/BCC
                  </Button>
                  <Button
                    size="small"
                    onClick={() => setShowTemplates(true)}
                    startIcon={<AccountBox />}
                    sx={{ ml: 2 }}
                  >
                    Use Template
                  </Button>
                </Box>

                {showCcBcc && (
                  <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Controller
                      name="cc"
                      control={control}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          label="CC"
                          fullWidth
                          placeholder="cc@example.com"
                          variant="outlined"
                        />
                      )}
                    />
                    <Controller
                      name="bcc"
                      control={control}
                      render={({ field }) => (
                        <TextField
                          {...field}
                          label="BCC"
                          fullWidth
                          placeholder="bcc@example.com"
                          variant="outlined"
                        />
                      )}
                    />
                  </Box>
                )}
              </Box>

              {/* Subject and Priority */}
              <Box sx={{ mb: 2, display: 'flex', gap: 2, alignItems: 'flex-start' }}>
                <Controller
                  name="subject"
                  control={control}
                  rules={{ required: 'Subject is required' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Subject"
                      fullWidth
                      error={!!errors.subject}
                      helperText={errors.subject?.message}
                      variant="outlined"
                    />
                  )}
                />
                <Controller
                  name="priority"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      select
                      label="Priority"
                      SelectProps={{ native: true }}
                      sx={{ minWidth: 120 }}
                      variant="outlined"
                    >
                      <option value="low">Low</option>
                      <option value="normal">Normal</option>
                      <option value="high">High</option>
                      <option value="urgent">Urgent</option>
                    </TextField>
                  )}
                />
              </Box>

              {/* Formatting Toolbar */}
              <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={richTextMode}
                      onChange={(e) => setRichTextMode(e.target.checked)}
                    />
                  }
                  label="Rich Text"
                />
                {richTextMode && (
                  <>
                    <Divider orientation="vertical" flexItem />
                    <IconButton size="small">
                      <FormatBold />
                    </IconButton>
                    <IconButton size="small">
                      <FormatItalic />
                    </IconButton>
                    <IconButton size="small">
                      <FormatUnderlined />
                    </IconButton>
                    <IconButton size="small">
                      <InsertEmoticon />
                    </IconButton>
                  </>
                )}
              </Box>

              {/* Message Body */}
              <Box sx={{ mb: 2 }}>
                <Controller
                  name="body"
                  control={control}
                  rules={{ required: 'Message body is required' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Message"
                      fullWidth
                      multiline
                      rows={12}
                      error={!!errors.body}
                      helperText={errors.body?.message}
                      variant="outlined"
                      placeholder="Type your message here..."
                    />
                  )}
                />
              </Box>

              {/* Attachments */}
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Button
                    variant="outlined"
                    startIcon={<AttachFile />}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    Attach Files
                  </Button>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={scheduleSend}
                        onChange={(e) => setScheduleSend(e.target.checked)}
                      />
                    }
                    label="Schedule Send"
                  />
                  {scheduleSend && (
                    <TextField
                      type="datetime-local"
                      label="Send At"
                      InputLabelProps={{ shrink: true }}
                      variant="outlined"
                      size="small"
                    />
                  )}
                </Box>

                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  style={{ display: 'none' }}
                  onChange={handleFileUpload}
                />

                {attachments.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Attachments ({attachments.length})
                    </Typography>
                    <List dense>
                      {attachments.map((attachment) => (
                        <ListItem
                          key={attachment.id}
                          sx={{
                            border: 1,
                            borderColor: 'divider',
                            borderRadius: 1,
                            mb: 1,
                          }}
                        >
                          <ListItemIcon>
                            <AttachFile />
                          </ListItemIcon>
                          <ListItemText
                            primary={attachment.name}
                            secondary={`${formatFileSize(attachment.size)} • ${attachment.type}`}
                          />
                          <ListItemSecondaryAction>
                            <IconButton
                              edge="end"
                              onClick={() => handleRemoveAttachment(attachment.id)}
                            >
                              <Delete />
                            </IconButton>
                          </ListItemSecondaryAction>
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
              </Box>

              {/* Action Buttons */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Chip
                    label={`Priority: ${watch('priority')}`}
                    color={getPriorityColor(watch('priority')) as any}
                    variant="outlined"
                    size="small"
                  />
                </Box>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button
                    variant="outlined"
                    onClick={() => router.back()}
                    disabled={loading}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Save />}
                    onClick={handleSubmit(handleSaveDraft)}
                    disabled={loading}
                  >
                    Save Draft
                  </Button>
                  <Button
                    type="submit"
                    variant="contained"
                    startIcon={<Send />}
                    disabled={loading}
                  >
                    {loading ? 'Sending...' : 'Send Email'}
                  </Button>
                </Box>
              </Box>
            </form>
          </CardContent>
        </Card>
      </Box>

      {/* Templates Dialog */}
      <Dialog
        open={showTemplates}
        onClose={() => setShowTemplates(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Choose Email Template</DialogTitle>
        <DialogContent>
          <List>
            {templates.map((template) => (
              <ListItem
                key={template.id}
                button
                onClick={() => handleUseTemplate(template)}
                sx={{
                  border: 1,
                  borderColor: 'divider',
                  borderRadius: 1,
                  mb: 1,
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemText
                  primary={template.name}
                  secondary={
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        Subject: {template.subject}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {template.body.substring(0, 100)}...
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowTemplates(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ComposePage;