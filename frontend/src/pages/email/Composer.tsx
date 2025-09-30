/**
 * Email Composer Component
 * Handles new email composition, replies, and forwards with attachment support
 */

import React, { useState, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Send as SendIcon,
  AttachFile as AttachFileIcon,
  Close as CloseIcon,
  Save as SaveIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import dynamic from 'next/dynamic';
import 'react-quill/dist/quill.snow.css';
import { emailService, ComposeEmail, Email, MailAccount, EmailAddress } from '../../services/emailService';

const ReactQuill = dynamic(() => import('react-quill'), { ssr: false });

interface ComposerProps {
  mode: 'new' | 'reply' | 'replyAll' | 'forward';
  originalEmail?: Email;
  selectedAccount?: MailAccount;
  onClose?: () => void;
  onSent?: (emailId: number) => void;
}

interface AttachmentFile extends File {
  id: string;
}

const Composer: React.FC<ComposerProps> = ({
  mode,
  originalEmail,
  selectedAccount,
  onClose,
  onSent
}) => {
  const [to, setTo] = useState<EmailAddress[]>([]);
  const [cc, setCc] = useState<EmailAddress[]>([]);
  const [bcc, setBcc] = useState<EmailAddress[]>([]);
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [priority, setPriority] = useState<'low' | 'normal' | 'high' | 'urgent'>('normal');
  const [attachments, setAttachments] = useState<AttachmentFile[]>([]);
  const [showCC, setShowCC] = useState(false);
  const [showBCC, setShowBCC] = useState(false);
  const [templateDialogOpen, setTemplateDialogOpen] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  // Fetch available email templates
  const { data: templates = [] } = useQuery({
    queryKey: ['email-templates'],
    queryFn: emailService.getEmailTemplates
  });

  // Send email mutation
  const sendEmailMutation = useMutation({
    mutationFn: (emailData: ComposeEmail) => {
      if (!selectedAccount) {
        throw new Error('No account selected');
      }
      return emailService.composeEmail(emailData, selectedAccount.id);
    },
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['emails'] });
      onSent?.(result.email_id);
      onClose?.();
    }
  });

  // Initialize composer based on mode
  React.useEffect(() => {
    if (!originalEmail) return;

    switch (mode) {
      case 'reply':
        setTo([{ email: originalEmail.from_address, name: originalEmail.from_name }]);
        setSubject(originalEmail.subject.startsWith('Re: ') ? originalEmail.subject : `Re: ${originalEmail.subject}`);
        setBody(generateReplyBody(originalEmail));
        break;
      
      case 'replyAll':
        setTo([{ email: originalEmail.from_address, name: originalEmail.from_name }]);
        setCc(originalEmail.cc_addresses || []);
        setSubject(originalEmail.subject.startsWith('Re: ') ? originalEmail.subject : `Re: ${originalEmail.subject}`);
        setBody(generateReplyBody(originalEmail));
        setShowCC(true);
        break;
      
      case 'forward':
        setSubject(originalEmail.subject.startsWith('Fwd: ') ? originalEmail.subject : `Fwd: ${originalEmail.subject}`);
        setBody(generateForwardBody(originalEmail));
        break;
    }
  }, [mode, originalEmail]);

  const generateReplyBody = (email: Email) => {
    const date = new Date(email.received_at).toLocaleString();
    const from = email.from_name ? `${email.from_name} <${email.from_address}>` : email.from_address;
    
    return `\n\n--- Original Message ---\nFrom: ${from}\nDate: ${date}\nSubject: ${email.subject}\n\n${email.body_text || email.body_html || ''}`;
  };

  const generateForwardBody = (email: Email) => {
    const date = new Date(email.received_at).toLocaleString();
    const from = email.from_name ? `${email.from_name} <${email.from_address}>` : email.from_address;
    const to = email.to_addresses.map(addr => addr.name ? `${addr.name} <${addr.email}>` : addr.email).join(', ');
    
    return `--- Forwarded Message ---\nFrom: ${from}\nTo: ${to}\nDate: ${date}\nSubject: ${email.subject}\n\n${email.body_text || email.body_html || ''}`;
  };

  const handleAddRecipient = (type: 'to' | 'cc' | 'bcc', email: string) => {
    const newRecipient = { email: email.trim() };
    switch (type) {
      case 'to':
        setTo([...to, newRecipient]);
        break;
      case 'cc':
        setCc([...cc, newRecipient]);
        break;
      case 'bcc':
        setBcc([...bcc, newRecipient]);
        break;
    }
  };

  const handleRemoveRecipient = (type: 'to' | 'cc' | 'bcc', index: number) => {
    switch (type) {
      case 'to':
        setTo(to.filter((_, i) => i !== index));
        break;
      case 'cc':
        setCc(cc.filter((_, i) => i !== index));
        break;
      case 'bcc':
        setBcc(bcc.filter((_, i) => i !== index));
        break;
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      const newAttachments: AttachmentFile[] = Array.from(files).map(file => 
        Object.assign(file, { id: Math.random().toString(36).substr(2, 9) })
      );
      setAttachments([...attachments, ...newAttachments]);
    }
  };

  const handleRemoveAttachment = (id: string) => {
    setAttachments(attachments.filter(att => att.id !== id));
  };

  const handleApplyTemplate = async (template: any) => {
    try {
      const templateData = {}; // You can populate this with relevant data
      const result = await emailService.applyTemplate(template.id, templateData);
      setSubject(result.subject);
      setBody(result.body_html);
      setTemplateDialogOpen(false);
    } catch (error) {
      console.error('Failed to apply template:', error);
    }
  };

  const handleSend = () => {
    const emailData: ComposeEmail = {
      to,
      cc: cc.length > 0 ? cc : undefined,
      bcc: bcc.length > 0 ? bcc : undefined,
      subject,
      body_html: body,
      attachments: attachments.length > 0 ? attachments : undefined,
      priority: priority !== 'normal' ? priority : undefined,
      reply_to_id: mode === 'reply' || mode === 'replyAll' ? originalEmail?.id : undefined,
      forward_from_id: mode === 'forward' ? originalEmail?.id : undefined
    };

    sendEmailMutation.mutate(emailData);
  };

  const canSend = to.length > 0 && subject.trim() && body.trim() && selectedAccount && !sendEmailMutation.isPending;

  const quillModules = {
    toolbar: [
      [{ 'header': '1'}, {'header': '2'}, { 'font': [] }],
      [{size: []}],
      ['bold', 'italic', 'underline', 'strike', 'blockquote'],
      [{'list': 'ordered'}, {'list': 'bullet'}, 
       {'indent': '-1'}, {'indent': '+1'}],
      ['link', 'image'],
      ['clean']
    ]
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <CardContent sx={{ pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">
            {mode === 'new' && 'New Message'}
            {mode === 'reply' && 'Reply'}
            {mode === 'replyAll' && 'Reply All'}
            {mode === 'forward' && 'Forward'}
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              size="small"
              onClick={() => setTemplateDialogOpen(true)}
              disabled={templates.length === 0}
            >
              Templates
            </Button>
            
            <IconButton onClick={onClose} size="small">
              <CloseIcon />
            </IconButton>
          </Box>
        </Box>

        {sendEmailMutation.error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            Failed to send email: {(sendEmailMutation.error as Error).message}
          </Alert>
        )}

        {/* Account selector */}
        {!selectedAccount && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            Please select an email account to send from
          </Alert>
        )}
      </CardContent>

      {/* Compose form */}
      <CardContent sx={{ flex: 1, pt: 0, display: 'flex', flexDirection: 'column' }}>
        {/* Recipients */}
        <Box sx={{ mb: 2 }}>
          <TextField
            fullWidth
            label="To"
            size="small"
            placeholder="Enter email addresses separated by commas"
            sx={{ mb: 1 }}
            onKeyPress={(e) => {
              if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                const value = (e.target as HTMLInputElement).value.trim();
                if (value && value.includes('@')) {
                  handleAddRecipient('to', value);
                  (e.target as HTMLInputElement).value = '';
                }
              }
            }}
          />
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
            {to.map((recipient, index) => (
              <Chip
                key={index}
                label={recipient.name ? `${recipient.name} <${recipient.email}>` : recipient.email}
                onDelete={() => handleRemoveRecipient('to', index)}
                size="small"
              />
            ))}
          </Box>

          <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
            <Button size="small" onClick={() => setShowCC(!showCC)}>
              {showCC ? 'Hide CC' : 'CC'}
            </Button>
            <Button size="small" onClick={() => setShowBCC(!showBCC)}>
              {showBCC ? 'Hide BCC' : 'BCC'}
            </Button>
          </Box>

          {showCC && (
            <>
              <TextField
                fullWidth
                label="CC"
                size="small"
                placeholder="CC recipients"
                sx={{ mb: 1 }}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' || e.key === ',') {
                    e.preventDefault();
                    const value = (e.target as HTMLInputElement).value.trim();
                    if (value && value.includes('@')) {
                      handleAddRecipient('cc', value);
                      (e.target as HTMLInputElement).value = '';
                    }
                  }
                }}
              />
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                {cc.map((recipient, index) => (
                  <Chip
                    key={index}
                    label={recipient.name ? `${recipient.name} <${recipient.email}>` : recipient.email}
                    onDelete={() => handleRemoveRecipient('cc', index)}
                    size="small"
                    variant="outlined"
                  />
                ))}
              </Box>
            </>
          )}

          {showBCC && (
            <>
              <TextField
                fullWidth
                label="BCC"
                size="small"
                placeholder="BCC recipients"
                sx={{ mb: 1 }}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' || e.key === ',') {
                    e.preventDefault();
                    const value = (e.target as HTMLInputElement).value.trim();
                    if (value && value.includes('@')) {
                      handleAddRecipient('bcc', value);
                      (e.target as HTMLInputElement).value = '';
                    }
                  }
                }}
              />
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                {bcc.map((recipient, index) => (
                  <Chip
                    key={index}
                    label={recipient.name ? `${recipient.name} <${recipient.email}>` : recipient.email}
                    onDelete={() => handleRemoveRecipient('bcc', index)}
                    size="small"
                    variant="outlined"
                  />
                ))}
              </Box>
            </>
          )}
        </Box>

        {/* Subject and Priority */}
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            fullWidth
            label="Subject"
            size="small"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
          />
          
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Priority</InputLabel>
            <Select
              value={priority}
              label="Priority"
              onChange={(e) => setPriority(e.target.value as any)}
            >
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="normal">Normal</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="urgent">Urgent</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {/* Rich text editor */}
        <Box sx={{ flex: 1, mb: 2 }}>
          <ReactQuill
            value={body}
            onChange={setBody}
            modules={quillModules}
            style={{ height: '200px' }}
          />
        </Box>

        {/* Attachments */}
        {attachments.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" fontWeight="bold" gutterBottom>
              Attachments ({attachments.length})
            </Typography>
            <List dense>
              {attachments.map((file) => (
                <ListItem key={file.id} sx={{ border: 1, borderColor: 'divider', borderRadius: 1, mb: 0.5 }}>
                  <ListItemIcon>
                    <AttachFileIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={file.name}
                    secondary={`${Math.round(file.size / 1024)} KB • ${file.type || 'Unknown type'}`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      size="small"
                      onClick={() => handleRemoveAttachment(file.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        {/* Actions */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="contained"
              startIcon={sendEmailMutation.isPending ? <CircularProgress size={16} /> : <SendIcon />}
              onClick={handleSend}
              disabled={!canSend}
            >
              {sendEmailMutation.isPending ? 'Sending...' : 'Send'}
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<SaveIcon />}
              disabled={sendEmailMutation.isPending}
            >
              Save Draft
            </Button>
          </Box>

          <Box>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              style={{ display: 'none' }}
              onChange={handleFileSelect}
            />
            
            <IconButton
              onClick={() => fileInputRef.current?.click()}
              title="Attach files"
            >
              <AttachFileIcon />
            </IconButton>
          </Box>
        </Box>
      </CardContent>

      {/* Template Dialog */}
      <Dialog open={templateDialogOpen} onClose={() => setTemplateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Choose Email Template</DialogTitle>
        <DialogContent>
          <List>
            {templates.map((template) => (
              <ListItem 
                key={template.id}
                button 
                onClick={() => handleApplyTemplate(template)}
                sx={{ border: 1, borderColor: 'divider', borderRadius: 1, mb: 1 }}
              >
                <ListItemText
                  primary={template.name}
                  secondary={template.description}
                />
              </ListItem>
            ))}
          </List>
          
          {templates.length === 0 && (
            <Typography color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
              No email templates available
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTemplateDialogOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default Composer;