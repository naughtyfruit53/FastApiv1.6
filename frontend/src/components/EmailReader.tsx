/**
 * Email Reader Component
 * Displays email content and provides actions like reply, forward, etc.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Avatar,
  Chip,
  Divider,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Reply,
  ReplyAll,
  Forward,
  MarkEmailRead,
  MarkEmailUnread,
  Attachment,
  Download,
  Refresh
} from '@mui/icons-material';
import api from '../../lib/api';

interface EmailAttachment {
  id: number;
  filename: string;
  size_bytes: number;
  content_type: string;
  file_path: string | null;
}

interface EmailDetail {
  id: number;
  message_id: string;
  subject: string;
  from_address: string;
  from_name: string | null;
  to_addresses: string[];
  cc_addresses: string[] | null;
  bcc_addresses: string[] | null;
  sent_at: string;
  received_at: string;
  body_text: string | null;
  body_html: string | null;
  status: string;
  priority: string;
  is_flagged: boolean;
  is_important: boolean;
  folder: string | null;
  labels: string[] | null;
  size_bytes: number | null;
  has_attachments: boolean;
  attachments: EmailAttachment[];
}

interface EmailReaderProps {
  tokenId: number;
  messageId: number | null;
  onReply?: (messageId: number, subject: string, sender: string) => void;
  onClose?: () => void;
}

const EmailReader: React.FC<EmailReaderProps> = ({
  tokenId,
  messageId,
  onReply,
  onClose
}) => {
  const [email, setEmail] = useState<EmailDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [markingRead, setMarkingRead] = useState<boolean>(false);

  useEffect(() => {
    if (messageId && tokenId) {
      loadEmailDetail();
    }
  }, [messageId, tokenId]);

  const loadEmailDetail = async () => {
    if (!messageId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await api.get(`/api/v1/mail/emails/${messageId}`);

      setEmail(response.data);

      // Auto-mark as read if it's unread
      if (response.data.status === 'UNREAD') {
        markAsRead();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load email');
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async () => {
    if (!messageId || !email || email.status !== 'UNREAD') return;

    setMarkingRead(true);
    try {
      await api.put(`/api/v1/mail/emails/${messageId}`, { status: 'READ' });
      setEmail(prev => prev ? { ...prev, status: 'READ' } : null);
    } catch (err) {
      console.error('Failed to mark email as read:', err);
    } finally {
      setMarkingRead(false);
    }
  };

  const markAsUnread = async () => {
    if (!messageId || !email || email.status === 'UNREAD') return;

    try {
      await api.put(`/api/v1/mail/emails/${messageId}`, { status: 'UNREAD' });
      setEmail(prev => prev ? { ...prev, status: 'UNREAD' } : null);
    } catch (err) {
      console.error('Failed to mark email as unread:', err);
    }
  };

  const handleReply = () => {
    if (email && onReply) {
      onReply(email.id, email.subject, email.from_address);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch {
      return dateString;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getInitials = (email: string) => {
    const parts = email.split('@')[0].split('.');
    return parts.map(part => part.charAt(0).toUpperCase()).join('').slice(0, 2);
  };

  if (!messageId) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          height: '100%',
          color: 'text.secondary'
        }}
      >
        <Typography variant="h6">
          Select an email to read
        </Typography>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          height: '100%'
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert 
          severity="error" 
          action={
            <Button color="inherit" size="small" onClick={loadEmailDetail}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      </Box>
    );
  }

  if (!email) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          height: '100%'
        }}
      >
        <Typography variant="h6" color="text.secondary">
          Email not found
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100%', overflow: 'auto' }}>
      <Card sx={{ m: 2 }}>
        {/* Email Header */}
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
            <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
              {getInitials(email.from_address)}
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" sx={{ mb: 1 }}>
                {email.subject}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                From: {email.from_name || email.from_address}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                To: {email.to_addresses.join(', ')}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatDate(email.received_at)}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip 
                label={email.status} 
                size="small"
                color={email.status === 'UNREAD' ? 'primary' : 'default'}
              />
              {email.has_attachments && (
                <Chip 
                  icon={<Attachment />}
                  label={`${email.attachments.length}`}
                  size="small"
                  variant="outlined"
                />
              )}
            </Box>
          </Box>

          {/* Email Actions */}
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <Button
              size="small"
              startIcon={<Reply />}
              onClick={handleReply}
            >
              Reply
            </Button>
            <Button
              size="small"
              startIcon={<ReplyAll />}
              disabled
            >
              Reply All
            </Button>
            <Button
              size="small"
              startIcon={<Forward />}
              disabled
            >
              Forward
            </Button>
            <Divider orientation="vertical" flexItem />
            <IconButton
              size="small"
              onClick={email.status === 'READ' ? markAsUnread : markAsRead}
              disabled={markingRead}
            >
              <Tooltip title={email.status === 'READ' ? 'Mark as unread' : 'Mark as read'}>
                {email.status === 'READ' ? <MarkEmailUnread /> : <MarkEmailRead />}
              </Tooltip>
            </IconButton>
            <IconButton size="small" onClick={loadEmailDetail}>
              <Tooltip title="Refresh">
                <Refresh />
              </Tooltip>
            </IconButton>
          </Box>

          <Divider />

          {/* Email Content */}
          <Box sx={{ mt: 3 }}>
            {email.body_html ? (
              <Box
                component="div"
                dangerouslySetInnerHTML={{ __html: email.body_html }}
                sx={{
                  '& img': {
                    maxWidth: '100%',
                    height: 'auto'
                  },
                  '& a': {
                    color: 'primary.main'
                  }
                }}
              />
            ) : (
              <Typography
                component="pre"
                sx={{
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'inherit',
                  fontSize: 'inherit'
                }}
              >
                {email.body_text || 'No content to display'}
              </Typography>
            )}
          </Box>

          {/* Attachments */}
          {email.attachments.length > 0 && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Attachments ({email.attachments.length})
              </Typography>
              <List dense>
                {email.attachments.map((attachment) => (
                  <ListItem
                    key={attachment.id}
                    sx={{
                      border: 1,
                      borderColor: 'divider',
                      borderRadius: 1,
                      mb: 1
                    }}
                  >
                    <ListItemIcon>
                      <Attachment />
                    </ListItemIcon>
                    <ListItemText
                      primary={attachment.filename}
                      secondary={`${attachment.content_type} • ${formatFileSize(attachment.size_bytes)}`}
                    />
                    <IconButton
                      edge="end"
                      disabled={!attachment.file_path}
                      title="Download attachment"
                      onClick={() => window.open(attachment.file_path || '', '_blank')}
                    >
                      <Download />
                    </IconButton>
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default EmailReader;