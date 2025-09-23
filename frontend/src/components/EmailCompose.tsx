/**
 * Email Compose Component
 * Provides email composition functionality for OAuth-connected accounts
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Alert,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Send,
  Close
} from '@mui/icons-material';
import { useOAuth } from '../hooks/useOAuth';
import api from '../../lib/api';

interface UserEmailToken {
  id: number;
  email_address: string;
  display_name: string | null;
  provider: string;
  is_active: boolean;
}

interface EmailComposeProps {
  open: boolean;
  onClose: () => void;
  replyTo?: {
    messageId: string;
    subject: string;
    sender: string;
    recipients: string[];
  };
  onSuccess?: () => void;
}

const EmailCompose: React.FC<EmailComposeProps> = ({
  open,
  onClose,
  replyTo,
  onSuccess
}) => {
  const [tokens, setTokens] = useState<UserEmailToken[]>([]);
  const [selectedTokenId, setSelectedTokenId] = useState<number | null>(null);
  const [to, setTo] = useState<string>('');
  const [cc, setCc] = useState<string>('');
  const [bcc, setBcc] = useState<string>('');
  const [subject, setSubject] = useState<string>('');
  const [body, setBody] = useState<string>('');
  const [htmlBody, setHtmlBody] = useState<string>('');
  const [useHtml, setUseHtml] = useState<boolean>(false);
  const [showCc, setShowCc] = useState<boolean>(false);
  const [showBcc, setShowBcc] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const { getUserTokens } = useOAuth();

  useEffect(() => {
    if (open) {
      loadEmailTokens();
      
      // Pre-fill for reply
      if (replyTo) {
        setTo(replyTo.sender);
        setSubject(replyTo.subject.startsWith('Re:') ? replyTo.subject : `Re: ${replyTo.subject}`);
        setBody(`\n\n--- Original Message ---\nFrom: ${replyTo.sender}\nSubject: ${replyTo.subject}\n\n`);
      }
    }
  }, [open, replyTo]);

  const loadEmailTokens = async () => {
    try {
      const userTokens = await getUserTokens();
      const activeTokens = userTokens.filter(token => token.is_active);
      setTokens(activeTokens);
      
      if (activeTokens.length === 1) {
        setSelectedTokenId(activeTokens[0].id);
      }
    } catch (err: any) {
      setError('Failed to load email accounts');
    }
  };

  const handleSend = async () => {
    if (!selectedTokenId) {
      setError('Please select an email account');
      return;
    }

    if (!to.trim()) {
      setError('Please enter at least one recipient');
      return;
    }

    if (!subject.trim()) {
      setError('Please enter a subject');
      return;
    }

    if (!body.trim() && !htmlBody.trim()) {
      setError('Please enter email content');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.post(`/api/v1/mail/tokens/${selectedTokenId}/emails/send`, {
        to: to.split(',').map(email => email.trim()).filter(email => email),
        cc: cc ? cc.split(',').map(email => email.trim()).filter(email => email) : undefined,
        bcc: bcc ? bcc.split(',').map(email => email.trim()).filter(email => email) : undefined,
        subject: subject,
        body_text: body,
        body_html: useHtml ? htmlBody : undefined,
        in_reply_to_id: replyTo ? replyTo.messageId : undefined
      });

      if (response.data.success) {
        setSuccess('Email sent successfully!');
        setTimeout(() => {
          onSuccess?.();
          handleClose();
        }, 1500);
      } else {
        setError(response.data.message || 'Failed to send email');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to send email');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setTo('');
    setCc('');
    setBcc('');
    setSubject('');
    setBody('');
    setHtmlBody('');
    setUseHtml(false);
    setShowCc(false);
    setShowBcc(false);
    setError(null);
    setSuccess(null);
    setSelectedTokenId(null);
    onClose();
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { minHeight: '600px' }
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">
            {replyTo ? 'Reply' : 'Compose Email'}
          </Typography>
          <Button onClick={handleClose} sx={{ minWidth: 'auto', p: 1 }}>
            <Close />
          </Button>
        </Box>
      </DialogTitle>

      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        <Grid container spacing={2}>
          {/* Email Account Selection */}
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>From Email Account</InputLabel>
              <Select
                value={selectedTokenId || ''}
                onChange={(e) => setSelectedTokenId(Number(e.target.value))}
                disabled={loading || tokens.length === 0}
              >
                {tokens.map((token) => (
                  <MenuItem key={token.id} value={token.id}>
                    <Box>
                      <Typography variant="body2">
                        {token.display_name || token.email_address}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {token.email_address} ({token.provider})
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Recipients */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="To"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              placeholder="recipient1@example.com, recipient2@example.com"
              helperText="Separate multiple recipients with commas"
              disabled={loading}
            />
          </Grid>

          {/* CC/BCC Toggle */}
          <Grid item xs={12}>
            <Box display="flex" gap={2}>
              <Button
                size="small"
                onClick={() => setShowCc(!showCc)}
                variant={showCc ? 'contained' : 'outlined'}
              >
                CC
              </Button>
              <Button
                size="small"
                onClick={() => setShowBcc(!showBcc)}
                variant={showBcc ? 'contained' : 'outlined'}
              >
                BCC
              </Button>
            </Box>
          </Grid>

          {/* CC Field */}
          {showCc && (
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="CC"
                value={cc}
                onChange={(e) => setCc(e.target.value)}
                placeholder="cc1@example.com, cc2@example.com"
                disabled={loading}
              />
            </Grid>
          )}

          {/* BCC Field */}
          {showBcc && (
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="BCC"
                value={bcc}
                onChange={(e) => setBcc(e.target.value)}
                placeholder="bcc1@example.com, bcc2@example.com"
                disabled={loading}
              />
            </Grid>
          )}

          {/* Subject */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              disabled={loading}
            />
          </Grid>

          {/* HTML Toggle */}
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={useHtml}
                  onChange={(e) => setUseHtml(e.target.checked)}
                />
              }
              label="Rich HTML Content"
            />
          </Grid>

          {/* Email Body */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={12}
              label={useHtml ? "HTML Content" : "Email Content"}
              value={useHtml ? htmlBody : body}
              onChange={(e) => useHtml ? setHtmlBody(e.target.value) : setBody(e.target.value)}
              placeholder={useHtml ? 
                "Enter HTML content..." : 
                "Enter your email message..."
              }
              disabled={loading}
            />
          </Grid>

          {/* TODO: Attachments */}
          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary">
              Attachments are not yet supported
            </Typography>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleSend}
          disabled={loading || !selectedTokenId || tokens.length === 0}
          startIcon={loading ? <CircularProgress size={20} /> : <Send />}
        >
          {loading ? 'Sending...' : 'Send Email'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EmailCompose;