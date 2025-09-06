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
  CardActions,
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
  Star,
  StarBorder,
  Attachment,
  Download,
  Refresh
} from '@mui/icons-material';

interface EmailAttachment {
  id: string;
  name: string;
  content_type: string;
  size: number;
  download_url?: string;
}

interface EmailDetail {
  id: string;
  subject: string;
  sender: string;
  recipients: string[];
  received_at: string;
  body_preview?: string;
  is_read: boolean;
  has_attachments: boolean;
  folder: string;
  body_html?: string;
  body_text?: string;
  attachments: EmailAttachment[];
  headers?: Record<string, string>;
}

interface EmailReaderProps {
  tokenId: number;
  messageId: string | null;
  onReply?: (messageId: string, subject: string, sender: string) => void;
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
      const response = await fetch(
        `/api/v1/email/tokens/${tokenId}/emails/${messageId}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to load email');
      }

      const emailData = await response.json();
      setEmail(emailData);

      // Auto-mark as read if it's unread
      if (!emailData.is_read) {
        markAsRead();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load email');
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async () => {
    if (!messageId || !email || email.is_read) return;

    setMarkingRead(true);
    try {
      const response = await fetch(
        `/api/v1/email/tokens/${tokenId}/emails/${messageId}/mark-read`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      if (response.ok) {
        setEmail(prev => prev ? { ...prev, is_read: true } : null);
      }
    } catch (err) {
      console.error('Failed to mark email as read:', err);
    } finally {
      setMarkingRead(false);
    }
  };

  const markAsUnread = async () => {
    if (!messageId || !email || !email.is_read) return;

    try {
      const response = await fetch(
        `/api/v1/email/tokens/${tokenId}/emails/${messageId}/mark-unread`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      if (response.ok) {
        setEmail(prev => prev ? { ...prev, is_read: false } : null);
      }
    } catch (err) {
      console.error('Failed to mark email as unread:', err);
    }
  };

  const handleReply = () => {
    if (email && onReply) {
      onReply(email.id, email.subject, email.sender);
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
              {getInitials(email.sender)}
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" sx={{ mb: 1 }}>
                {email.subject}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                From: {email.sender}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                To: {email.recipients.join(', ')}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {formatDate(email.received_at)}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip 
                label={email.is_read ? 'Read' : 'Unread'} 
                size="small"
                color={email.is_read ? 'default' : 'primary'}
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
              onClick={email.is_read ? markAsUnread : markAsRead}
              disabled={markingRead}
            >
              <Tooltip title={email.is_read ? 'Mark as unread' : 'Mark as read'}>
                {email.is_read ? <MarkEmailUnread /> : <MarkEmailRead />}
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
                {email.body_text || email.body_preview || 'No content to display'}
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
                      primary={attachment.name}
                      secondary={`${attachment.content_type} • ${formatFileSize(attachment.size)}`}
                    />
                    <IconButton
                      edge="end"
                      disabled={!attachment.download_url}
                      title="Download attachment"
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