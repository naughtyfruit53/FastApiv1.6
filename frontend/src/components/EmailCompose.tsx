/**
 * Email Compose Component
 * Allows composing and sending emails with rich text, attachments, etc.
 */

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Send,
  Save,
  AttachFile,
  Close,
  Add,
  Delete,
  Schedule
} from '@mui/icons-material';
import 'react-quill/dist/quill.snow.css';
import { useOAuth } from '../hooks/useOAuth';
import api from '../lib/api';

const ReactQuill = dynamic(() => import('react-quill'), { ssr: false });

interface UserEmailToken {
  id: number;
  email_address: string;
  display_name: string | null;
}

interface EmailTemplate {
  id: number;
  name: string;
  subject_template: string;
  body_html_template: string;
}

const EmailCompose: React.FC<{ open: boolean; onClose: () => void }> = ({ open, onClose }) => {
  const { getUserTokens } = useOAuth();
  const [tokens, setTokens] = useState<UserEmailToken[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<number | null>(null);
  const [to, setTo] = useState<string[]>([]);
  const [cc, setCc] = useState<string[]>([]);
  const [bcc, setBcc] = useState<string[]>([]);
  const [toInput, setToInput] = useState('');
  const [ccInput, setCcInput] = useState('');
  const [bccInput, setBccInput] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [attachments, setAttachments] = useState<File[]>([]);
  const [templates, setTemplates] = useState<EmailTemplate[] | null>(null);
  const [showTemplates, setShowTemplates] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const tokensRes = await getUserTokens();
        setTokens(tokensRes);
        if (tokensRes.length > 0) {
          setSelectedAccount(tokensRes[0].id);
        }

        const templatesRes = await api.get('/mail/templates');
        setTemplates(templatesRes.data || []);
      } catch (err) {
        setError('Failed to load data');
        setTemplates([]);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [getUserTokens]);

  const handleAddRecipient = (type: 'to' | 'cc' | 'bcc', email: string) => {
    if (email.trim()) {
      if (type === 'to') setTo([...to, email.trim()]);
      if (type === 'cc') setCc([...cc, email.trim()]);
      if (type === 'bcc') setBcc([...bcc, email.trim()]);
    }
  };

  const handleRemoveRecipient = (type: 'to' | 'cc' | 'bcc', index: number) => {
    if (type === 'to') setTo(to.filter((_, i) => i !== index));
    if (type === 'cc') setCc(cc.filter((_, i) => i !== index));
    if (type === 'bcc') setBcc(bcc.filter((_, i) => i !== index));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setAttachments([...attachments, ...Array.from(e.target.files)]);
    }
  };

  const handleRemoveAttachment = (index: number) => {
    setAttachments(attachments.filter((_, i) => i !== index));
  };

  const handleSend = async () => {
    if (!selectedAccount) {
      setError('Please select an account');
      return;
    }

    if (to.length === 0) {
      setError('Please add at least one recipient');
      return;
    }

    setSending(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('to_addresses', JSON.stringify(to));
      formData.append('cc_addresses', JSON.stringify(cc));
      formData.append('bcc_addresses', JSON.stringify(bcc));
      formData.append('subject', subject);
      formData.append('body_html', body);

      attachments.forEach((file) => {
        formData.append('attachments', file);
      });

      await api.post(`/mail/tokens/${selectedAccount}/emails/send`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to send email');
    } finally {
      setSending(false);
    }
  };

  const handleSaveDraft = async () => {
    // Implement draft saving logic
    console.log('Saving draft...');
  };

  const handleUseTemplate = (template: EmailTemplate) => {
    setSubject(template.subject_template);
    setBody(template.body_html_template);
    setShowTemplates(false);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Typography variant="h6" sx={{ mb: 2 }}>
        New Message
      </Typography>

      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>From</InputLabel>
        <Select
          value={selectedAccount || ''}
          onChange={(e) => setSelectedAccount(Number(e.target.value))}
          label="From"
        >
          {tokens.map((token) => (
            <MenuItem key={token.id} value={token.id}>
              {token.display_name || token.email_address}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {/* To */}
      <TextField
        fullWidth
        label="To"
        variant="outlined"
        sx={{ mb: 2 }}
        value={toInput}
        onChange={(e) => setToInput(e.target.value)}
        InputProps={{
          endAdornment: (
            <Button
              size="small"
              onClick={() => {
                handleAddRecipient('to', toInput);
                setToInput('');
              }}
            >
              Add
            </Button>
          )
        }}
      />
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
        {to.map((email, index) => (
          <Chip
            key={index}
            label={email}
            onDelete={() => handleRemoveRecipient('to', index)}
            deleteIcon={<Close />}
          />
        ))}
      </Box>

      {/* CC */}
      <TextField
        fullWidth
        label="Cc"
        variant="outlined"
        sx={{ mb: 2 }}
        value={ccInput}
        onChange={(e) => setCcInput(e.target.value)}
        InputProps={{
          endAdornment: (
            <Button
              size="small"
              onClick={() => {
                handleAddRecipient('cc', ccInput);
                setCcInput('');
              }}
            >
              Add
            </Button>
          )
        }}
      />
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
        {cc.map((email, index) => (
          <Chip
            key={index}
            label={email}
            onDelete={() => handleRemoveRecipient('cc', index)}
            deleteIcon={<Close />}
          />
        ))}
      </Box>

      {/* BCC */}
      <TextField
        fullWidth
        label="Bcc"
        variant="outlined"
        sx={{ mb: 2 }}
        value={bccInput}
        onChange={(e) => setBccInput(e.target.value)}
        InputProps={{
          endAdornment: (
            <Button
              size="small"
              onClick={() => {
                handleAddRecipient('bcc', bccInput);
                setBccInput('');
              }}
            >
              Add
            </Button>
          )
        }}
      />
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
        {bcc.map((email, index) => (
          <Chip
            key={index}
            label={email}
            onDelete={() => handleRemoveRecipient('bcc', index)}
            deleteIcon={<Close />}
          />
        ))}
      </Box>

      <TextField
        fullWidth
        label="Subject"
        variant="outlined"
        value={subject}
        onChange={(e) => setSubject(e.target.value)}
        sx={{ mb: 2 }}
      />

      <ReactQuill
        theme="snow"
        value={body}
        onChange={setBody}
        modules={{
          toolbar: [
            [{ 'header': [1, 2, false] }],
            ['bold', 'italic', 'underline', 'strike'],
            ['link', 'image'],
            [{ 'list': 'ordered'}, { 'list': 'bullet' }],
            ['clean']
          ]
        }}
        style={{ height: '400px', marginBottom: '50px' }}
      />

      {/* Attachments */}
      <Box sx={{ mt: 2 }}>
        <Button
          variant="outlined"
          startIcon={<AttachFile />}
          component="label"
        >
          Add Attachment
          <input
            type="file"
            hidden
            multiple
            onChange={handleFileChange}
          />
        </Button>
        <List dense sx={{ mt: 1 }}>
          {attachments.map((file, index) => (
            <ListItem key={index}>
              <ListItemIcon>
                <AttachFile />
              </ListItemIcon>
              <ListItemText primary={file.name} />
              <IconButton edge="end" onClick={() => handleRemoveAttachment(index)}>
                <Delete />
              </IconButton>
            </ListItem>
          ))}
        </List>
      </Box>

      {/* Actions */}
      <Box sx={{ display: 'flex', gap: 2, mt: 4 }}>
        <Button
          variant="contained"
          startIcon={<Send />}
          onClick={handleSend}
          disabled={sending}
        >
          Send
        </Button>
        <Button
          variant="outlined"
          startIcon={<Save />}
          onClick={handleSaveDraft}
          disabled={sending}
        >
          Save Draft
        </Button>
        <Button
          variant="outlined"
          onClick={() => setShowTemplates(true)}
        >
          Use Template
        </Button>
        <Button
          variant="outlined"
          startIcon={<Schedule />}
          disabled
        >
          Schedule
        </Button>
      </Box>

      {/* Templates Dialog */}
      <Dialog
        open={showTemplates}
        onClose={() => setShowTemplates(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Select Template</DialogTitle>
        <DialogContent>
          <List>
            {templates?.map((template) => (
              <ListItem
                key={template.id}
                button
                onClick={() => handleUseTemplate(template)}
              >
                <ListItemText primary={template.name} />
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

export default EmailCompose;